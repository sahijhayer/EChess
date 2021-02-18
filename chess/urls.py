from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("play", views.play, name="play"),
    path("login", views.loginPage, name="login"),
    path("logout", views.logoutUser, name="logout"),
    path("register", views.registerPage, name="register"),
    path("games", views.pastGames, name="games"),
    path("games/<int:game_id>", views.game, name="game")
]
