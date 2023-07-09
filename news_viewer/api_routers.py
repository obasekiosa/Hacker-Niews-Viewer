from rest_framework import routers
from . import views_api


router = routers.DefaultRouter()
router.register(r'stories', views_api.StoryViewSet)
router.register(r"comments", views_api.CommentViewSet)