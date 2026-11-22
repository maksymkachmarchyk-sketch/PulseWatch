from rest_framework import serializers
from checks.models import CheckResult


class CheckResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckResult
        fields = '__all__'
        read_only_fields = [
            'id',
            'monitor',
            'status_code',
            'response_time',
            'is_success',
            'error_message',
            'checked_at',
        ]
