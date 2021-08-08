from django.urls import path

from .views import UserView, LoginView, CourseView, CourseDetailView, ActivityView

# ----------------------------------


urlpatterns = [
    path("accounts/", UserView.as_view()),
    path("login/", LoginView.as_view()),
    path("courses/", CourseView.as_view()),
    path("courses/<int:course_id>/registrations/", CourseDetailView.as_view()),
    path("courses/<int:course_id>/", CourseDetailView.as_view()),
    path("activities/", ActivityView.as_view()),
]
