"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from tournament.views import (
    fixtures,
    match_detail,
    player_stats,
    standings,
    team_detail,
    teams,
    home,
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("standings/", standings, name="standings"),
    path("teams/", teams, name="teams"),
    path("matches/<int:pk>/", match_detail, name="match_detail"),
    path("teams/<int:pk>/", team_detail, name="team_detail"),
    path("fixtures/", fixtures, name="fixtures"),
    path("player-stats/", player_stats, name="player_stats"),
    path("", home, name="home"),
]
