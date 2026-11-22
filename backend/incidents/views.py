
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Incident
from .serializer import IncidentSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_list(request):
    incidents = Incident.objects.filter(
        monitor__user=request.user
    ).order_by('-started_at')

    monitor_id = request.query_params.get('monitor_id')

    if monitor_id:
        incidents = incidents.filter(monitor_id=monitor_id)

    serializer = IncidentSerializer(incidents, many=True)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_detail(request, pk):
    incident = get_object_or_404(
        Incident,
        id=pk,
        monitor__user=request.user
    )

    serializer = IncidentSerializer(incident)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )
