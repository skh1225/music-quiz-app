"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from music import views


router = DefaultRouter()
router.register('musics', views.MusicViewSet)
router.register('tags', views.TagViewSet)
router.register('singers', views.SingerViewSet)
router.register('rooms', views.RoomViewSet)

app_name = 'music'

urlpatterns = [
    path('', include(router.urls)),
]
