from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status 

from django.shortcuts import get_object_or_404

from monitors.models import Monitor
from .models import CheckResult
from .serializers import CheckResultSerializer
# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_history(request, monitor_id):
    monitor = get_object_or_404(
        Monitor, 
        id=monitor_id,
        user=request.user
        )
    check_result = CheckResult.objects.filter(monitor=monitor).order_by('-checked_at')
    serializer = CheckResultSerializer(many=True, instance=check_result)
    return Response(serializer.data,status=status.HTTP_200_OK)
