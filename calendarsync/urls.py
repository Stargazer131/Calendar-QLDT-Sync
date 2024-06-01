from django.contrib import admin
from django.urls import include, path
from sync import urls as sync_urls
from user import urls as user_urls
from google_calendar import urls as google_calendar_urls
from schedule import urls as schedule_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/synchronize-schedule-calendar/", include(sync_urls)),
    path("api/user/", include(user_urls)),
    path("api/google-calendar/", include(google_calendar_urls)),
    path("api/schedule/", include(schedule_urls)),
]
