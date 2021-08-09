from django.urls import path

from .views import (
    UserView,
    LoginView,
    CourseView,
    CourseDetailView,
    ActivityView,
    ActivityDetailView,
    SubmissionView,
    SubmissionDetailView,
)

# ----------------------------------


urlpatterns = [
    path("accounts/", UserView.as_view()),
    path("login/", LoginView.as_view()),
    path("courses/", CourseView.as_view()),
    path("courses/<int:course_id>/registrations/", CourseDetailView.as_view()),
    path("courses/<int:course_id>/", CourseDetailView.as_view()),
    path("activities/", ActivityView.as_view()),
    path("activities/<int:activity_id>/submissions/", ActivityDetailView.as_view()),
    path("submissions/", SubmissionView.as_view()),
    path("submissions/<int:submission_id>/", SubmissionDetailView.as_view()),
]
