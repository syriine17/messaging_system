from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Message, MessageThread


class MessageTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")

        # Create a message thread with participants
        self.thread = MessageThread.objects.create()
        self.thread.participants.add(self.user1, self.user2)

        # Create a message
        self.message = Message.objects.create(
            thread=self.thread, sender=self.user1, content="Hello World"
        )

        # Obtain a token for user1
        self.token = Token.objects.create(user=self.user1)

        # Initialize API client and authenticate with the token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_retrieve_threads(self):
        response = self.client.get("/api/threads/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json()[0])
        self.assertIn("participants", response.json()[0])
        self.assertIn("messages", response.json()[0])

    def test_search_in_threads(self):
        response = self.client.get("/api/search/", {"q": "Hello"})
        self.assertEqual(response.status_code, 200)
        messages = response.json()
        self.assertGreater(len(messages), 0)
        self.assertEqual(messages[0]["content"], "Hello World")

    def test_send_message(self):
        response = self.client.post(
            "/api/messages/", {"thread": self.thread.id, "content": "Hi there!"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.count(), 2)
        new_message = Message.objects.last()
        self.assertEqual(new_message.content, "Hi there!")
