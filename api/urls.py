from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    MessageThreadListCreateView,
    MessageListCreateView,
    SendMessageView,
    SearchMessagesView,
    UserCreateView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Messaging System API",
        default_version="v1",
        description="Messaging System API Mini Project",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("login/", ObtainAuthToken.as_view(), name="api_token_auth"),
    path("register/", UserCreateView.as_view(), name="user_register"),
    path("threads/", MessageThreadListCreateView.as_view(), name="threads"),
    path("messages/", MessageListCreateView.as_view(), name="messages"),
    path("send/", SendMessageView.as_view(), name="send_message"),
    path("search/", SearchMessagesView.as_view(), name="search"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
