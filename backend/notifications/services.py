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
        send_notification.delay(notification.id)
    except Exception:
        pass

    return notification