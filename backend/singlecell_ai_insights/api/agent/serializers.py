from rest_framework import serializers


class AgentChatRequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    metric_key = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
