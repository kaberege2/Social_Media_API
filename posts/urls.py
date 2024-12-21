from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, PostFeed

router =  DefaultRouter()
router.register(r"posts_all", PostViewSet, basename="post-viewset-list")

urlpatterns = [
    path("", include(router.urls)),
    path("feed/", PostFeed.as_view(), name="post_feed"),
]