from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from monitors.models import Monitor
from monitors.serializers import MonitorSerializer
# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def monitor_list(request):
    if request.method == 'GET':
        monitors = Monitor.objects.filter(user=request.user)
        serializer = MonitorSerializer(monitors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = MonitorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def monitor_detail(request, pk):
    monitor = get_object_or_404(
        Monitor,
        id=pk,
        user=request.user
    )
    if request.method == 'GET':
        serializer = MonitorSerializer(monitor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = MonitorSerializer(monitor, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        serializer = MonitorSerializer(
            monitor,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        monitor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def monitor_create(request):
    serializer = MonitorSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)