from rest_framework import serializers
from monitors.models import Monitor


class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = '__all__'
        read_only_fields = [
            'id',
            'user',
            'checks_count',
            'created_at',
            'updated_at',
        ]

    def validate_max_checks(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError(
                'Maximum checks must be at least 1.'
            )

        return value

    def validate_interval(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Interval must be at least 1 second.'
            )

        return value

    def validate_timeout(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Timeout must be at least 1 second.'
            )

        return value