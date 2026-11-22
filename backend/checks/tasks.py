from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

import redis

from .services import run_check
from .models import CheckResult
from monitors.models import Monitor
from incidents.services import process_check_result


redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)


@shared_task
def review_site(monitor_id):
    try:
        monitor = Monitor.objects.get(id=monitor_id)
    except Monitor.DoesNotExist:
        return 'Monitor does not exist'

    lock = redis_client.lock(
        f'pulsewatch:monitor:{monitor_id}:check',
        timeout=max(monitor.timeout + 30, 60)
    )

    if not lock.acquire(blocking=False):
        return 'Monitor check is already running'

    try:
        try:
            monitor = Monitor.objects.get(id=monitor_id)
        except Monitor.DoesNotExist:
            return 'Monitor does not exist'

        if not monitor.is_active:
            return 'Monitor is inactive'

        if (
            monitor.max_checks is not None
            and monitor.checks_count >= monitor.max_checks
        ):
            monitor.is_active = False
            monitor.save(update_fields=['is_active'])
            return 'Monitor reached maximum checks'

        check = run_check(monitor)
        process_check_result(check)

        monitor.checks_count += 1

        if (
            monitor.max_checks is not None
            and monitor.checks_count >= monitor.max_checks
        ):
            monitor.is_active = False

        monitor.save(update_fields=['checks_count', 'is_active'])

        return check.id

    finally:
        try:
            lock.release()
        except redis.exceptions.RedisError:
            pass


@shared_task
def dispatch_checks():
    monitors = Monitor.objects.filter(is_active=True)

    for monitor in monitors:
        last_check = CheckResult.objects.filter(
            monitor=monitor
        ).order_by('-checked_at').first()

        if last_check is None:
            review_site.delay(monitor.id)
            continue

        next_check = last_check.checked_at + timedelta(
            seconds=monitor.interval
        )
        if timezone.now() >= next_check:
            review_site.delay(monitor.id)