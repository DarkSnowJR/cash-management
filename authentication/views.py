from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import permissions
from . import serializers


class RegisterAPIView(generics.GenericAPIView):
    """
    post: Register a new user
    """
    serializer_class = serializers.RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    """
    post: Login user and return JWT token
    """
    serializer_class = serializers.LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    """
    post: Logout user and blacklist JWT token
    """
    serializer_class = serializers.LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
