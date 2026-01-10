from django.urls import path
from . import views


app_name = "timeline"

urlpatterns = [
    path('', views.time_line_view, name='time_line'), # Root URL shows the map
]