from .models import Conversation
from django.db import transaction


def get_or_create_conversation(user_a, user_b):
    """
    Returns existing conversation between two users
    or creates one if it doesn't exist.
    """

    # Prevent self-chat
    if user_a == user_b:
        raise ValueError("Users cannot start conversation with themselves")

    # Ensure ordering BEFORE querying
    if user_a.id > user_b.id:
        user_a, user_b = user_b, user_a

    conversation = Conversation.objects.filter(
        user1=user_a,
        user2=user_b
    ).first()

    if conversation:
        return conversation

    # Atomic to prevent race condition
    with transaction.atomic():
        conversation = Conversation.objects.create(
            user1=user_a,
            user2=user_b
        )

    return conversation
