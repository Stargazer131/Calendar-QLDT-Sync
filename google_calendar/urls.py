from django.urls import path
from google_calendar.views import UploadApiView, VerifyGmailApiView


urlpatterns = [
    path("upload/", UploadApiView.as_view()),
    path("verify-gmail/", VerifyGmailApiView.as_view()),
]
