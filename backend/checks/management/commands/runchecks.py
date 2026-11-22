import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from checks.models import CheckResult
from checks.services import run_check
from incidents.services import process_check_result
from monitors.models import Monitor


class Command(BaseCommand):
    help = 'Run monitor checks in this process (no Redis / Celery needed). For local development.'

    def add_arguments(self, parser):
        parser.add_argument('--every', type=int, default=10, help='seconds between scheduler ticks')
        parser.add_argument('--once', action='store_true', help='run one tick and exit')

    def handle(self, *args, **opts):
        from PulseWatch.celery import app
        app.conf.task_always_eager = True  # notification tasks run inline instead of via Redis

        self.stdout.write('Running checks in-process. Ctrl+C to stop.')
        while True:
            self.tick()
            if opts['once']:
                break
            time.sleep(opts['every'])

    def tick(self):
        for monitor in Monitor.objects.filter(is_active=True):
            if monitor.max_checks is not None and monitor.checks_count >= monitor.max_checks:
                monitor.is_active = False
                monitor.save(update_fields=['is_active'])
                continue

            last = CheckResult.objects.filter(monitor=monitor).order_by('-checked_at').first()
            if last and timezone.now() < last.checked_at + timedelta(seconds=monitor.interval):
                continue

            check = run_check(monitor)
            process_check_result(check)

            monitor.checks_count += 1
            if monitor.max_checks is not None and monitor.checks_count >= monitor.max_checks:
                monitor.is_active = False
            monitor.save(update_fields=['checks_count', 'is_active'])

            self.stdout.write(f'{monitor.name}: {"OK" if check.is_success else "FAIL"} '
                              f'({check.status_code or check.error_message}, {check.response_time} ms)')
