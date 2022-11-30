from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path("feeds", UserFeeds.as_view()),
    path("posts", PostView.as_view()),
    path('profiles', ProfileView.as_view()),
    path('profiles/<int:id>', ProfileView.as_view()),
]
