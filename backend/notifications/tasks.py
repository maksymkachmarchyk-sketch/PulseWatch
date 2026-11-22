from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Notification


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_notification(self, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return 'Notification does not exist'

    if notification.is_sent:
        return 'Notification already sent'

    try:
        if notification.channel == 'email':
            send_mail(
                subject='PulseWatch Alert',
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                fail_silently=False
            )
        else:
            raise ValueError('Unsupported notification channel')

        notification.is_sent = True
        notification.sent_at = timezone.now()
        notification.error_message = ''
        notification.save()

        return 'Notification sent'

    except Exception as error:
        notification.error_message = str(error)
        notification.save(update_fields=['error_message'])

        if notification.channel == 'email':
            raise self.retry(exc=error)

        raise
