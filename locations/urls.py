from django.urls import path
from django.views.generic.base import TemplateView
from . import views


app_name = "locations"

urlpatterns = [
    path('upload/', views.upload_data, name='upload_data'),
    path('', views.map_view, name='map_view'), # Root URL shows the map
    path('google_photos/', views.google_photos_map, name='google_photos'), # Root URL shows the map
    path('people_images/', views.PeopleImages.as_view(), name='people_images'), # Root URL shows the map
    path('metromap/', TemplateView.as_view(template_name="locations/metro_map2.html", content_type="text/html"), name="metromap"),
]