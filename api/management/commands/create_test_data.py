from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import MessageThread, Message
import random


class Command(BaseCommand):
    help = "Create test users, message threads, and messages"

    def handle(self, *args, **kwargs):
        # Create users
        user1 = User.objects.create_user(username="user1", password="password1")
        user2 = User.objects.create_user(username="user2", password="password2")
        user3 = User.objects.create_user(username="user3", password="password3")
        users = [user1, user2, user3]

        self.stdout.write(self.style.SUCCESS("Successfully created users"))

        # Create message threads
        threads = []
        for i in range(3):
            thread = MessageThread.objects.create()
            # Add 2 random users to the thread
            thread.participants.add(*random.sample(users, 2))
            threads.append(thread)

        self.stdout.write(self.style.SUCCESS("Successfully created message threads"))

        # Create messages
        for thread in threads:
            # Create 5 messages per thread
            for i in range(5):
                sender = random.choice(thread.participants.all())
                content = f"Test message {i+1} in thread {thread.id}"
                Message.objects.create(thread=thread, sender=sender, content=content)

        self.stdout.write(self.style.SUCCESS("Successfully created messages"))
