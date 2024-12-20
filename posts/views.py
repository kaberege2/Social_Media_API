from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .serializers import PostSerializer
from .models import Post

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

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