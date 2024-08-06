import logging
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.tasks import send_email_task
from .models import Message, MessageThread
from .serializers import MessageSerializer, MessageThreadSerializer, UserSerializer

# Configure logger
logger = logging.getLogger(__name__)


class UserCreateView(generics.CreateAPIView):
    """
    Create a new user.
    ---
    request:
      description: User registration
      serializer: UserSerializer
    response:
      description: Success message
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        try:
            serializer.save()
            logger.info(f"User created: {serializer.validated_data['username']}")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise


class SendMessageView(generics.CreateAPIView):
    """
    Send a message to another user.
    ---
    request:
      description: Message details
      serializer: MessageSerializer
    response:
      description: Success message
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            recipient_id = self.request.data.get("recipient")
            recipient = get_object_or_404(User, id=recipient_id)

            # Find or create a thread
            thread, created = MessageThread.objects.get_or_create(
                participants__in=[self.request.user, recipient]
            )
            if not created:
                # Add the recipient to the thread if not already present
                if not thread.participants.filter(id=recipient.id).exists():
                    thread.participants.add(recipient)

            serializer.save(sender=self.request.user, thread=thread)

            # Send an email notification asynchronously
            send_email_task.delay(
                subject="New Message Notification",
                message=f"You have a new message from {self.request.user.username}: {self.request.data.get('content')}",
                from_email="no-reply@example.com",
                recipient_list=[recipient.email],
            )
            logger.info(
                f"Message sent from {self.request.user.username} to {recipient.username}"
            )
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise


class MessageThreadListCreateView(generics.ListAPIView):
    """
    Retrieve message threads for the logged-in user.
    ---
    response:
      description: List of message threads
      serializer: MessageThreadSerializer
    """

    serializer_class = MessageThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return MessageThread.objects.filter(participants=user)


class MessageListCreateView(generics.ListCreateAPIView):
    """
    Retrieve messages in threads for the logged-in user and create new messages.
    ---
    request:
      description: Message details
      serializer: MessageSerializer
    response:
      description: List of messages or success message
      serializer: MessageSerializer
    """

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        cache_key = f"user_messages_{user.id}"
        messages = cache.get(cache_key)

        if not messages:
            try:
                threads = MessageThread.objects.filter(participants=user)
                messages = Message.objects.filter(thread__in=threads)
                # Caching the list of messages for a user can improve
                # performance if the same data is requested frequently.
                cache.set(cache_key, messages, timeout=60 * 15)  # Cache for 15 minutes
                logger.info(f"Messages cached for user {user.id}")
            except Exception as e:
                logger.error(f"Error retrieving or caching messages: {str(e)}")
                raise

        return messages

    def perform_create(self, serializer):
        try:
            thread_id = self.request.data.get("thread")
            thread = get_object_or_404(MessageThread, id=thread_id)
            serializer.save(sender=self.request.user, thread=thread)
            logger.info(
                f"Message created in thread {thread_id} by user {self.request.user.id}"
            )
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise


class SearchMessagesView(generics.ListAPIView):
    """
    Search for messages based on content within threads for the logged-in user.

    This endpoint allows users to search for messages by content and optionally
    filter messages by thread.

    ---
    request:
      description:
        - The search parameters are provided as URL query parameters.
        - Example: `?q=search_term&thread_id=1`
      parameters:
        - name: q
          type: string
          required: false
          description: The term or phrase to search for within message contents.
        - name: thread_id
          type: integer
          required: false
          description: Filter messages that belong to this specific thread.
    response:
      description:
        - A list of messages matching the search criteria.
        - Messages are returned in a list, and each message object contains details such as sender, content, and creation time.
      serializer: MessageSerializer
    """

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        query = self.request.query_params.get("q", "")
        thread_id = self.request.query_params.get("thread_id", None)

        try:
            # Get all threads the user is part of
            threads = MessageThread.objects.filter(participants=user)

            # Base queryset for messages in these threads
            queryset = Message.objects.filter(thread__in=threads)

            # Filter by content if provided
            if query:
                queryset = queryset.filter(content__icontains=query)

            # Filter by thread ID if provided
            if thread_id:
                queryset = queryset.filter(thread_id=thread_id)

            logger.info(
                f"Search performed with query '{query}' and thread_id '{thread_id}'"
            )
            return queryset
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            raise
