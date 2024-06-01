from django.urls import path
from schedule.views import ScheduleApiView


urlpatterns = [
    path("", ScheduleApiView.as_view()),
]
