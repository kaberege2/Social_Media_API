from django.contrib import admin
from .models import Post, Comment, Like

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    list_filter = ('author', 'created_at', 'updated_at')
    search_fields = ("title", "content")

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'updated_at')
    list_filter = ('author', 'created_at', 'updated_at')
    search_fields = ("post", 'author', "content")

class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')
    list_filter = ('user', 'post')
    search_fields = ('user', 'post')


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)