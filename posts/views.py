from django.shortcuts import render, get_object_or_404
from rest_framework import filters, views, viewsets, status, generics
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .serializers import PostSerializer
from .models import Post
from django.contrib.auth import authenticate, get_user_model
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework

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