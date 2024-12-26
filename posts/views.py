from django.shortcuts import render, get_object_or_404
from rest_framework import filters, views, viewsets, status, generics
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .serializers import PostSerializer, CommentSerializer
from .models import Post, Comment, Like
from django.contrib.auth import authenticate, get_user_model
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework
from rest_framework.response import Response
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

User = get_user_model()  # Custom user model

class PostPagination(PageNumberPagination):
    page_size = 10

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
    filter_backends = [rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'created_at']
    search_fields = ['title', 'content']
    ordering_fields = ['id', 'title', 'created_at']
    ordering = ['id']
    

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Check if the user is the author before updating
        if self.get_object().author != self.request.user:
            raise PermissionDenied("You can only update your own posts!")
        serializer.save()

    def perform_destroy(self, instance):
        # Check if the user is the author before deleting
        if instance.author != self.request.user:
            raise PermissionDenied("You can only delete your own posts!")
        instance.delete()

class PostFeed(generics.ListAPIView):
    #queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
    filter_backends = [rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'created_at']
    search_fields = ['title', 'content']
    ordering_fields = ['id', 'title', 'created_at']
    ordering = ["-created_at"]

    def get_queryset(self):
        following_users = self.request.user.following.all()
        feed = Post.objects.filter(author__in=following_users).order_by('-created_at')
        return feed

class CommentViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
     # Enable Filtering, Searching, and Ordering
    filter_backends = [rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Define the filter fields
    filterset_fields = ['content', 'created_at']
    search_fields = ['content']
    ordering_fields = ['id', 'content', 'created_at']
    ordering = ['id']  # Default ordering by id

    def perform_create(self, serializer):
        # Save the comment with the logged-in user as the author
        comment = serializer.save(author=self.request.user)

        # Create a notification for the post author (notify them about the new comment)
        post = comment.post  # comment is linked to a post
        if post.author != self.request.user:
            # Notify the post author about the new comment
            Notification.objects.create(
                recipient=post.author,  # The user who owns the post
                actor=self.request.user,  # The user who made the comment
                verb='commented on your post',  # Action description
                target_content_type=ContentType.objects.get_for_model(Post),  # Content type of the post
                target_object_id=post.id  # The ID of the post
            )

    def perform_update(self, serializer):
        # Check if the user is the author before updating
        if self.get_object().author != self.request.user:
            raise PermissionDenied("You can only update your own posts.")
        serializer.save()

    def perform_destroy(self, instance):
        # Check if the user is the author before deleting
        if instance.author != self.request.user:
            raise PermissionDenied("You can only delete your own posts.")
        instance.delete()

class LikePostView(views.APIView):
    def post(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        # Check if the user is trying to like their own post
        if post.author == user:
            return Response({'detail': 'You cannot like your own post.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create a Like object
        like, created = Like.objects.get_or_create(user=user, post=post)
        
        if not created:
            return Response({'detail': 'You already liked this post.'}, status=status.HTTP_400_BAD_REQUEST)
         
         # Create a notification for the post's author when a post is liked
        notification = Notification(
            recipient=post.author,  # The author of the post
            actor=user,             # The user who liked the post
            verb='liked your post', # Verb explaining the action
            # ContentType to link the notification to the Post model
            target_content_type=ContentType.objects.get_for_model(Post),  # The content type of the Post model
            target_object_id=post.id,  # The specific post that was liked
        )
        notification.save()
        
        return Response({'detail': 'You liked this post.'}, status=status.HTTP_201_CREATED)

class UnlikePostView(views.APIView):
    def delete(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        # Check if the user is trying to unlike their own post
        if post.author == user:
            return Response({'detail': 'You cannot unlike your own post.'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to get the Like object, or return a 404 error if it doesn't exist
        try:
            like = Like.objects.get(user=user, post=post)  # This will raise Like.DoesNotExist if no like exists
            like.delete()  # If found, delete the like
            return Response({'detail': 'You unliked this post.'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'detail': 'You have not liked this post yet.'}, status=status.HTTP_400_BAD_REQUEST)
