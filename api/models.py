from django.db import models
from django.contrib.auth.models import User


class MessageThread(models.Model):
    participants = models.ManyToManyField(User)


class Message(models.Model):
    thread = models.ForeignKey(
        MessageThread, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"From {self.sender} in thread {self.thread.id} at {self.created_at}"
