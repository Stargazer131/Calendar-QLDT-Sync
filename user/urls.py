from django.urls import path
from user.views import VerifyAccountApiView


urlpatterns = [
    path("verify-account/", VerifyAccountApiView.as_view()),
]
