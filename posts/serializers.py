from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like

# Create your models here.
User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)

    class Meta:
         model = Comment
         fields = "__all__"

class PostSerializer(serializers.ModelSerializer):
    # Serializing 'author' as the user's ID
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    media = serializers.ImageField(required=False)
    
    # Serializing 'created_at' and 'updated_at' as ISO format date-time strings
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'media', 'created_at', 'updated_at', "comments"]

    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value

class LikeSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = "__all__"