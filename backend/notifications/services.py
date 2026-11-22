import os
import traceback

from .models import Notification
from .tasks import send_notification


def create_notification(user, incident, message, channel='email'):
    notification = Notification.objects.create(
        user=user,
        incident=incident,
        channel=channel,
        message=message
    )

    try:
        if os.getenv('NOTIFY_SYNC', '').lower() == 'true':
            # no Celery broker (e.g. single-container deploy): send right here
            send_notification.apply(args=[notification.id])
        else:
            send_notification.delay(notification.id)
    except Exception:
        traceback.print_exc()  # visible in the logs instead of being swallowed

    return notification
