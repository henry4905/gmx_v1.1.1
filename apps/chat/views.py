from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Message, Conversation
from .services import get_or_create_conversation
from django.contrib.auth import get_user_model
from django.db.models import Q

from django.http import Http404
User = get_user_model()


@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    conversation = get_or_create_conversation(request.user, other_user)

    return redirect("chat_room", conversation_id=conversation.id)





@login_required
def chat_room(request, conversation_id=None):

    conversation = None
    messages = []

    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)

        # Security check
        if request.user not in [conversation.user1, conversation.user2]:
            raise Http404("Conversation not found")

        messages = conversation.messages.select_related("sender").order_by("timestamp")

    return render(request, "chat/chat_room.html", {
        "conversation": conversation,
        "messages": messages,
        "conversations": Conversation.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        ).order_by("-created_at")
    })
