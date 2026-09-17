from django.urls import path

from backend.api.views import section

urlpatterns = [path("<str:name>", section), path("api/<str:name>", section)]
