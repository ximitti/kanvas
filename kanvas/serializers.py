from rest_framework import serializers

# -----------------------------------------------


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    is_superuser = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)


class UserSimpleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CourseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    users = UserSimpleSerializer(many=True, read_only=True)


class RegistrationSerializer(serializers.Serializer):
    user_ids = serializers.ListField()


class SubmissionSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    grade = serializers.IntegerField()
    repo = serializers.CharField()
    user_id = serializers.ReadOnlyField()
    activity_id = serializers.ReadOnlyField()


class ActivitySerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    title = serializers.CharField()
    points = serializers.IntegerField()
    submissions = SubmissionSerializer(many=True, read_only=True)
