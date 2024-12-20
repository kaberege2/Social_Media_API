from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router =  DefaultRouter()
router.register(r"posts_all", PostViewSet, basename="post-viewset-list")

urlpatterns = [
    path("", include(router.urls)),
]