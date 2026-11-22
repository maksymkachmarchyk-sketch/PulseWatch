from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .tokens import email_verification_token
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    CustomTokenObtainPairSerializer,
)


User = get_user_model()


def blacklist_user_tokens(user):
    tokens = OutstandingToken.objects.filter(user=user)

    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    user = serializer.save()

    if settings.AUTO_VERIFY_USERS:
        user.is_active = True
        user.save(update_fields=['is_active'])

        return Response(
            {'message': 'Registration successful. You can sign in now.'},
            status=status.HTTP_201_CREATED
        )

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verification_url = (
        f'{settings.FRONTEND_BASE_URL}/verify-email'
        f'?uid={uid}&token={token}'
    )

    try:
        send_mail(
            subject='PulseWatch - Verify your email',
            message=(
                f'Welcome to PulseWatch!\n\n'
                f'Click the link below to verify your email:\n'
                f'{verification_url}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        user.delete()
        return Response(
            {'error': 'Could not send the verification email. Check the '
                      'EMAIL_* settings in .env (or set AUTO_VERIFY_USERS=True '
                      'for local development).'},
            status=status.HTTP_502_BAD_GATEWAY
        )

    return Response(
        {'message': 'Registration successful. Check your email.'},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid verification link.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if email_verification_token.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])

        return Response({
            'message': 'Email successfully verified.'
        })

    return Response(
        {'error': 'Verification link is invalid or expired.'},
        status=status.HTTP_400_BAD_REQUEST
    )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']

    user = User.objects.filter(
        email__iexact=email,
        is_active=True
    ).first()

    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        reset_url = (
            f'{settings.FRONTEND_BASE_URL}/reset-password'
            f'?uid={uid}&token={token}'
        )

        send_mail(
            subject='PulseWatch - Password reset',
            message=(
                f'You requested a password reset.\n\n'
                f'Open this link to continue:\n{reset_url}\n\n'
                f'This link expires in 24 hours.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    return Response({
        'message': (
            'If an account with this email exists, '
            'a reset link has been sent.'
        )
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    if request.method == 'GET':
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')

        if not uid or not token:
            return Response(
                {'error': 'UID and token are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    else:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid reset link.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    token_generator = PasswordResetTokenGenerator()

    if not token_generator.check_token(user, token):
        return Response(
            {'error': 'Reset link is invalid or expired.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'GET':
        return Response({
            'message': 'Reset link is valid. Submit a new password using POST.'
        })

    new_password = serializer.validated_data['new_password']

    try:
        validate_password(new_password, user)

    except ValidationError as error:
        return Response(
            {'new_password': error.messages},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save(update_fields=['password'])

    blacklist_user_tokens(user)

    return Response({
        'message': 'Password successfully changed.'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save()
    blacklist_user_tokens(request.user)

    return Response({
        'message': 'Password successfully changed.'
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    serializer = UserProfileSerializer(
        request.user,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
