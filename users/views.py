from django.shortcuts import render
from rest_framework import status, views, generics
from django.contrib.auth import authenticate
from .serializers import RegistrationSerializer, LoginSerializer, UserProfileSerializer, UserProfileUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class RegisterView(views.APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data["username"], password=serializer.validated_data["password"])
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({"message": "user logged-in successfully", 'refresh': str(refresh), 'access': str(refresh.access_token),}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credetials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        instance = request.user
        serializer = UserProfileUpdateSerializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            # Save the updated user instance and return a response
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # If the serializer is not valid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileDelete(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        instance = request.user
        instance.delete()
        return Response({"Message": "Account was deleted successfully"}, status=status.HTTP_204_NO_CONTENT)