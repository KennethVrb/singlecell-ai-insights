from rest_framework import serializers

from ..models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = [
            'run_id',
            'name',
            'status',
            'pipeline',
            'created_at',
            'started_at',
            'completed_at',
            's3_report_key',
            'metadata',
        ]
