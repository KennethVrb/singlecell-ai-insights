from rest_framework import serializers

from singlecell_ai_insights.models import Message


class AgentChatRequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    metric_key = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'role',
            'content',
            'citations',
            'notes',
            'metric_key',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
