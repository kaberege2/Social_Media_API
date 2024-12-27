from django.shortcuts import render
from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.pagination import PageNumberPagination

# A custom pagination class for notifications
class NotificationPagination(PageNumberPagination):
    page_size = 10  # Define how many notifications per page (adjust as needed)
    page_size_query_param = 'page_size'  # Allow the client to override page_size via query param
    max_page_size = 100  # Set a maximum page size

# This view handles the listing of notifications for an authenticated user
class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        """
        Overriding list to fetch and return unread notifications prominently at the top.
        """
        user = request.user
        
        # Fetch unread notifications first, then read notifications
        unread_notifications = Notification.objects.filter(recipient=user, is_read=False).order_by('-timestamp')
        read_notifications = Notification.objects.filter(recipient=user, is_read=True).order_by('-timestamp')

        # Serialize unread and read notifications
        unread_serializer = NotificationSerializer(unread_notifications, many=True)
        read_serializer = NotificationSerializer(read_notifications, many=True)

        # Return the response, showcasing unread notifications first
        return Response({
            'unread_notifications': unread_serializer.data,  # Unread first
            'read_notifications': read_serializer.data,      # Read after
        }, status=status.HTTP_200_OK)

# View to mark a specific notification as read or unread
class MarkNotificationReadView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            # Attempt to get the notification for the user
            notification = Notification.objects.get(id=pk, recipient=request.user)
            notification.is_read = True  # Mark as read
            notification.save()
            return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            # If notification is not found, return a 404 error
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            # Attempt to get the notification for the user
            notification = Notification.objects.get(id=pk, recipient=request.user)
            notification.is_read = False  # Mark as unread
            notification.save()
            return Response({"message": "Notification marked as unread"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            # If notification is not found, return a 404 error
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
