from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Message, MessageThread
from .serializers import MessageSerializer, MessageThreadSerializer, UserSerializer


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
        # Get all threads the user is part of
        threads = MessageThread.objects.filter(participants=user)
        # Get all messages in these threads
        return Message.objects.filter(thread__in=threads)

    def perform_create(self, serializer):
        thread_id = self.request.data.get("thread")
        thread = get_object_or_404(MessageThread, id=thread_id)
        serializer.save(sender=self.request.user, thread=thread)


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

        return queryset
