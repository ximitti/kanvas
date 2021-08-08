from django.db import models
from django.contrib.auth.models import User

# ---------------------------


class Course(models.Model):
    name = models.CharField(max_length=255, unique=True)

    users = models.ManyToManyField(User, related_name="courses")

    class Meta:
        db_table = "courses"


class Activity(models.Model):
    title = models.CharField(max_length=255, unique=True)
    points = models.IntegerField()

    class Meta:
        db_table = "activities"


class Submission(models.Model):
    grade = models.IntegerField(null=True)
    repo = models.CharField(max_length=255)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name="submissions"
    )

    class Meta:
        db_table = "submissions"
