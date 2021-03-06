from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db.models import ObjectDoesNotExist

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

from .models import Course, Activity, Submission

from .serializers import (
    UserSerializer,
    LoginSerializer,
    CourseSerializer,
    RegistrationSerializer,
    ActivitySerializer,
    SubmissionSerializer,
    SubmissionGradeSerializer,
)

from .permissions import IsInstructor, IsFacilitador, IsStudent, IsInstructorAndReadOnly

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
    permission_classes = [IsInstructorAndReadOnly]

    def post(self, request):

        serialized = CourseSerializer(data=request.data)

        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        course_data = serialized.validated_data

        course = Course.objects.get_or_create(**course_data)[0]

        serialized = CourseSerializer(course)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def get(self, request):

        courses = Course.objects.all()

        serialized = CourseSerializer(courses, many=True)

        return Response(serialized.data, status=status.HTTP_200_OK)


class CourseDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsInstructorAndReadOnly]

    def put(self, request, course_id=""):
        try:
            course = Course.objects.get(id=course_id)

            serialized = RegistrationSerializer(data=request.data)

            if not serialized.is_valid():
                return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

            users = request.data.pop("user_ids")

            register_list = []

            for user_id in users:
                try:
                    user = User.objects.get(id=user_id)

                    if user.is_superuser == True or user.is_staff == True:
                        return Response(
                            {"errors": "Only students can be enrolled in the course."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    register_list.append(user)

                except ObjectDoesNotExist as _:
                    return Response(
                        {"errors": "invalid user_id list"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            course.users.set(register_list)

            serialized = CourseSerializer(course)

            return Response(serialized.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist as _:
            return Response(
                {"errors": "invalid course_id"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, course_id=""):
        try:
            course = Course.objects.get(id=course_id)

            course.delete()

            return Response("", status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist as _:
            return Response(
                {"errors": "invalid course_id"}, status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, course_id=""):
        try:
            course = Course.objects.get(id=course_id)

            serialized = CourseSerializer(course)

            return Response(serialized.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist as _:
            return Response(
                {"errors": "invalid course_id"}, status=status.HTTP_404_NOT_FOUND
            )


class ActivityView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsInstructor | IsFacilitador]

    def post(self, request):
        serialized = ActivitySerializer(data=request.data)

        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        activity_data = serialized.validated_data

        activity = Activity.objects.filter(title=activity_data["title"]).first()
        print(activity)

        if activity:
            activity.points = activity_data["points"]
            activity.save()

        else:
            activity = Activity.objects.create(**activity_data)

        serialized = ActivitySerializer(activity)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def get(self, request):

        activities = Activity.objects.all()

        serialized = ActivitySerializer(activities, many=True)

        return Response(serialized.data, status=status.HTTP_200_OK)


class ActivityDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStudent]

    def post(self, request, activity_id=""):
        activity = get_object_or_404(Activity, id=activity_id)
        user = User.objects.get(id=request.user.id)

        serialized = SubmissionSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        submission_data = serialized.validated_data
        submission = Submission.objects.create(
            repo=submission_data["repo"], user=user, activity=activity
        )

        serialized = SubmissionSerializer(submission)

        return Response(serialized.data, status=status.HTTP_201_CREATED)


class SubmissionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsInstructor | IsFacilitador | IsStudent]

    def get(self, request):
        user = User.objects.get(id=request.user.id)

        if not user.is_staff and not user.is_superuser:
            print("student")
            submissions = Submission.objects.filter(user_id=user.id)

            serialized = SubmissionSerializer(submissions, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)

        submissions = Submission.objects.all()

        serialized = SubmissionSerializer(submissions, many=True)

        return Response(serialized.data, status=status.HTTP_200_OK)


class SubmissionDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsInstructor | IsFacilitador]

    def put(self, request, submission_id=""):
        submission = get_object_or_404(Submission, id=submission_id)

        serialized = SubmissionGradeSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        submission_data = serialized.validated_data

        submission.grade = submission_data["grade"]

        submission.save()

        serialized = SubmissionSerializer(submission)

        return Response(serialized.data, status=status.HTTP_200_OK)
