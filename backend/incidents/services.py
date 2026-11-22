from django.utils import timezone
from .models import Incident


def process_check_result(check):
    from notifications.services import create_notification

    incident = Incident.objects.filter(
        monitor=check.monitor,
        resolved_at__isnull=True
    ).first()

    if not check.is_success:
        if incident is None:
            reason = (
                f'HTTP {check.status_code}'
                if check.status_code is not None
                else check.error_message
            )

            incident = Incident.objects.create(
                monitor=check.monitor,
                reason=reason
            )

            create_notification(
                user=check.monitor.user,
                incident=incident,
                message=(
                    f'Your website {check.monitor.url} is down. '
                    f'Reason: {reason}'
                )
            )

    elif incident is not None:
        incident.resolved_at = timezone.now()
        incident.save(update_fields=['resolved_at'])

        create_notification(
            user=check.monitor.user,
            incident=incident,
            message=(
                f'Your website {check.monitor.url} is back online.'
            )
        )
