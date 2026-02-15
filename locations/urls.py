from django.urls import path
from django.views.generic.base import TemplateView
from . import views


app_name = "locations"

urlpatterns = [
    path('upload/', views.upload_data, name='upload_data'),
    path('', views.people_album_urls, name='people_album_urls'), # Root URL shows the map
    path('map_view/', views.map_view, name='map_view'), # Root URL shows the map
    path('google_photos/', views.google_photos_map, name='google_photos'),
    path('people_images/', views.PeopleImages.as_view(), name='people_images'), 
    path('slides/', views.SlideShowView.as_view(), name='slideshow'),
    path('people_videos/', views.PeopleVideos.as_view(), name='people_videos'), 
    path('people_videos_short/', views.PeopleVideos_short.as_view(), name='people_videos_short'), 
    path('image_with_description/', views.ImageWithDescription.as_view(), name='image_with_description'), 
    path('location_album/', views.LocationAlbum.as_view(), name='location_album'),
    path('location_album_urls/', views.location_album_urls, name='location_album_urls'),
    # path('location_people_album_urls/', views.location_people_album_urls, name='location_people_album_urls'),
    path('download/<int:media_id>/', views.download_media, name='download_media'),
    path('metromap/', TemplateView.as_view(template_name="locations/metro_map2.html", content_type="text/html"), name="metromap"),
]

Forms_URLs = [
    path('url_create/', views.UrlCreateView.as_view(), name='url_create'),
    path("url_update/<int:pk>", views.UrlUpdateView.as_view(), name="url_update"),
    path("people_name_update/<int:pk>", views.PeopleNameUpdateView.as_view(), name="people_name_update"),
]

urlpatterns += Forms_URLs

