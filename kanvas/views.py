from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, LoginSerializer

# ----------------------------------


class UserView(APIView):
    def post(self, request):
        serialized = UserSerializer(data=request.data)

        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=serialized.data["username"]).exists():
            return Response(
                {"error": "username already exists!"}, status=status.HTTP_409_CONFLICT
            )

        try:
            user = User(
                username=serialized.validated_data["username"],
                is_staff=serialized.validated_data["is_staff"],
                is_superuser=serialized.validated_data["is_superuser"],
            )

            password = serialized.validated_data["password"]

            validate_password(password, user)

            user.set_password(password)
            user.save()

            serialized = UserSerializer(user)

            return Response(serialized.data, status=status.HTTP_201_CREATED)

        except ValidationError as error:

            errors = {arg.code: arg.messages[0] for arg in error.args[0]}

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serialized = LoginSerializer(data=request.data)

        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(**serialized.validated_data)

        if user:
            token = Token.objects.get_or_create(user=user)[0]

            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_401_UNAUTHORIZED)
