from rest_framework import serializers
from incidents.models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = '__all__'
        read_only_fields = ['id', 'monitor', 'started_at', 'resolved_at', 'reason']