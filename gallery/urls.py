from django.urls import path
from . import views

app_name = "gallery"

urlpatterns = [
    path('', views.map_view, name='gallery_map'),
    path('upload/', views.upload_view, name='upload'),
]
