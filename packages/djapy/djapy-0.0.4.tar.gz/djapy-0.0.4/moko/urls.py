from django.urls import path, include
from moko.views import todo_view, sign_up_or_register_for_session
urlpatterns = [
    path('', todo_view, name='moko-home'),
    path('session/', sign_up_or_register_for_session, name='moko-session'),
]

