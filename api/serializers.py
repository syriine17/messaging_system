from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Message, MessageThread


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        ref_name = "User"


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    thread = serializers.PrimaryKeyRelatedField(queryset=MessageThread.objects.all())

    class Meta:
        model = Message
        fields = ["id", "sender", "thread", "content", "created_at"]
        ref_name = "Message"


class MessageThreadSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = ["id", "participants", "messages"]
        ref_name = "MessageThread"

    def get_messages(self, obj):
        return MessageSerializer(obj.messages.all(), many=True).data


class SearchMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "sender", "thread", "content", "created_at"]
        ref_name = "SearchMessage"
