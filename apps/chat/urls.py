from django.urls import path
from . import views
from django.urls import re_path
from . import consumers

urlpatterns = [
    path("", views.chat_room, {"conversation_id": None}, name="chat_home"),  # chat room առանց ընտրած conversation
    path("start/<int:user_id>/", views.start_chat, name="start_chat"),
    path("<int:conversation_id>/", views.chat_room, name="chat_room"),

    re_path(r'ws/chat/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),

]

