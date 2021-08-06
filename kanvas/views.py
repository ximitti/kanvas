from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .models import Course

from .serializers import (
    UserSerializer,
    LoginSerializer,
    CourseSerializer,
    RegistrationSerializer,
)

from .permissions import IsInstructor

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


class CourseView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsInstructor]

    def post(self, request):

        serialized = CourseSerializer(data=request.data)

        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        course_data = serialized.validated_data

        course = Course.objects.get_or_create(**course_data)[0]

        serialized = CourseSerializer(course)

        return Response(serialized.data, status=status.HTTP_201_CREATED)


class CourseRegistrationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsInstructor]

    def put(self, request, course_id=""):
        course = get_object_or_404(Course, id=course_id)

        serialized = RegistrationSerializer(data=request.data)

        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        users = request.data.pop("user_ids")

        register_list = []

        for user_id in users:
            user = get_object_or_404(User, id=user_id)

            if user.is_superuser == True or user.is_staff == True:
                return Response(
                    {"errors": "Only students can be enrolled in the course."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            register_list.append(user)

        course.users.set(register_list)

        serialized = CourseSerializer(course)

        return Response(serialized.data, status=status.HTTP_200_OK)
