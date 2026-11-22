from datetime import timedelta

from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from monitors.models import Monitor
from checks.models import CheckResult
from incidents.models import Incident


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    user = request.user

    monitors = Monitor.objects.filter(user=user)
    checks = CheckResult.objects.filter(monitor__user=user)
    incidents = Incident.objects.filter(monitor__user=user)

    # Monitor statistics

    monitors_total = monitors.count()
    monitors_active = monitors.filter(is_active=True).count()
    monitors_inactive = monitors.filter(is_active=False).count()

    # Check statistics

    check_stats = checks.aggregate(
        total=Count('id'),
        successful=Count('id', filter=Q(is_success=True)),
        failed=Count('id', filter=Q(is_success=False)),
        average_response_time=Avg('response_time'),
    )

    checks_total = check_stats['total']
    checks_successful = check_stats['successful']
    checks_failed = check_stats['failed']

    uptime_percentage = (
        round(checks_successful / checks_total * 100, 2)
        if checks_total > 0
        else None
    )

    average_response_time = check_stats['average_response_time']

    if average_response_time is not None:
        average_response_time = round(average_response_time, 2)

    # Incident statistics

    incidents_total = incidents.count()
    incidents_open = incidents.filter(resolved_at__isnull=True).count()
    incidents_resolved = incidents.filter(
        resolved_at__isnull=False
    ).count()

    # Last 7 days chart data

    today = timezone.localdate()
    start_date = today - timedelta(days=6)

    daily_checks = (
        checks
        .filter(checked_at__date__gte=start_date)
        .annotate(day=TruncDate('checked_at'))
        .values('day')
        .annotate(
            total=Count('id'),
            successful=Count('id', filter=Q(is_success=True)),
            failed=Count('id', filter=Q(is_success=False)),
            average_response_time=Avg('response_time'),
        )
        .order_by('day')
    )

    daily_data = {
        item['day']: item
        for item in daily_checks
    }

    chart_data = []

    for day_offset in range(7):
        current_day = start_date + timedelta(days=day_offset)
        item = daily_data.get(current_day)

        if item:
            avg_time = item['average_response_time']

            chart_data.append({
                'date': current_day.isoformat(),
                'total': item['total'],
                'successful': item['successful'],
                'failed': item['failed'],
                'average_response_time': (
                    round(avg_time, 2)
                    if avg_time is not None
                    else None
                ),
            })
        else:
            chart_data.append({
                'date': current_day.isoformat(),
                'total': 0,
                'successful': 0,
                'failed': 0,
                'average_response_time': None,
            })

    # Recent incidents

    recent_incidents = incidents.select_related(
        'monitor'
    ).order_by('-started_at')[:5]

    recent_incidents_data = [
        {
            'id': incident.id,
            'monitor_id': incident.monitor_id,
            'monitor_name': incident.monitor.name,
            'monitor_url': incident.monitor.url,
            'reason': incident.reason,
            'started_at': incident.started_at.isoformat(),
            'resolved_at': (
                incident.resolved_at.isoformat()
                if incident.resolved_at
                else None
            ),
            'is_resolved': incident.resolved_at is not None,
        }
        for incident in recent_incidents
    ]

    return Response(
        {
            'monitors': {
                'total': monitors_total,
                'active': monitors_active,
                'inactive': monitors_inactive,
            },
            'checks': {
                'total': checks_total,
                'successful': checks_successful,
                'failed': checks_failed,
                'uptime_percentage': uptime_percentage,
                'average_response_time': average_response_time,
            },
            'incidents': {
                'total': incidents_total,
                'open': incidents_open,
                'resolved': incidents_resolved,
            },
            'chart': chart_data,
            'recent_incidents': recent_incidents_data,
        },
        status=status.HTTP_200_OK
    )