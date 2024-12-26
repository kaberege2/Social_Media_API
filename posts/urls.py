from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, PostFeed, CommentViewset, LikePostView, UnlikePostView

router =  DefaultRouter()
router.register(r"posts_all", PostViewSet, basename="post-viewset-list")
router.register(r"comments_all", CommentViewset, basename="comment-viewset-list")

urlpatterns = [
    path("", include(router.urls)),
    path("feed/", PostFeed.as_view(), name="post_feed"),
    path('like/<int:post_id>/', LikePostView.as_view(), name='like_post'),
    path('unlike/<int:post_id>/', UnlikePostView.as_view(), name='unlike_post'),
]