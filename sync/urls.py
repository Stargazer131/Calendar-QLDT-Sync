from django.urls import path
from sync.views import StartSyncApiView


urlpatterns = [
    path("start/", StartSyncApiView.as_view()),
]
