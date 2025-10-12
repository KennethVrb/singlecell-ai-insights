from rest_framework import serializers

from singlecell_ai_insights.models.run import Run


class RunSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = [
            'pk',
            'run_id',
            'name',
            'status',
            'pipeline',
            'created_at',
            'started_at',
            'completed_at',
        ]


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = [
            *RunSummarySerializer.Meta.fields,
            'output_dir_bucket',
            'output_dir_key',
        ]
