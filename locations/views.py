from django.shortcuts import render, redirect
from datetime import datetime, date, timedelta
import os
from django.http import JsonResponse
from django.core.serializers import serialize
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import Substr, Concat, RowNumber, Replace, Cast, TruncMonth, Round, ExtractYear, ExtractMonth
from django.db.models import F, Q, Case, When, Subquery, OuterRef, Value,CharField, BooleanField, IntegerField, ExpressionWrapper, Window
from .models import LocationBatch, Place, GooglePhotos, PeopleNames
from .utils import parse_timeline_json, parse_kml, parse_saved_places_json, parse_labeled_places_json
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

# Define colors for each file type
BATCH_COLORS = {
    'timeline': 'red',
    'mymaps': 'blue',
    'saved': 'purple',
    'labeled': 'green'
}

# Define icons for each file type from Font Awesome
BATCH_ICONS = {
    'timeline': 'clock-o',
    'mymaps': 'map-marker',
    'saved': 'star',
    'labeled': 'tag'
}

def upload_data(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_type = request.POST.get('type')
        
        # Get the color for the batch, with a default
        batch_color = BATCH_COLORS.get(file_type, 'blue') # Default blue if type is somehow not in our map
        
        # Create a batch record
        batch = LocationBatch.objects.create(
            name=uploaded_file.name,
            file_type=file_type,
            color=batch_color
        )
        
        try:
            content = uploaded_file.read()
            
            if file_type == 'timeline':
                parse_timeline_json(batch, content)
            elif file_type == 'mymaps':
                parse_kml(batch, content)
            elif file_type == 'saved':
                parse_saved_places_json(batch, content)
            elif file_type == 'labeled':
                parse_labeled_places_json(batch, content)
            else:
                # If the file type is unknown, raise an error.
                raise ValueError(f"Unknown file type '{file_type}'.")
                
            return redirect('locations:map_view')
            
        except Exception as e:
            # simple error handling
            print(f"Error parsing file: {e}")
            batch.delete()
            return render(request, 'locations/upload.html', {'error': str(e)})

    return render(request, 'locations/upload.html')

def map_view(request):
    # Fetch all places and their batch color, grouped by batch
    batches = LocationBatch.objects.prefetch_related('places').all().order_by(
        'file_type', 'name')
    
    places_by_type = {}
    
    for batch in batches:
        file_type_display = batch.get_file_type_display()
        
        if file_type_display not in places_by_type:
            places_by_type[file_type_display] = {
                'color': BATCH_COLORS.get(batch.file_type, 'blue'),
                'icon': BATCH_ICONS.get(batch.file_type, 'info-circle'),
                'places': []
            }

        for place in batch.places.all():
            places_by_type[file_type_display]['places'].append({
                'name': place.name,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'address': place.address,
                'timestamp': place.timestamp,
            })
            
    # We also need a flat list for the JS markers
    flat_places_list = []
    for batch in batches:
        file_type = batch.file_type
        for place in batch.places.all():
            flat_places_list.append({
                'name': place.name,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'address': place.address,
                'timestamp': place.timestamp,
                'color': BATCH_COLORS.get(file_type, 'blue'),
                'icon': BATCH_ICONS.get(file_type, 'info-circle')
            })

    return render(request, 'locations/map.html', {
        'places_by_type_json': json.dumps(places_by_type, cls=DjangoJSONEncoder),
        'places_json': json.dumps(flat_places_list, cls=DjangoJSONEncoder),
        'total_place': len(flat_places_list)
    })
    
    
def google_photos_map(request):
    try:
        is_video = int(request.GET.get('is_video'))
        if is_video:
            media_items = GooglePhotos.objects.filter(Q(title__endswith='.mp4')|Q(title__endswith='.MOV'))
    except:
        media_items = GooglePhotos.objects.all()
        is_video = False
        
    
    media_items = media_items.annotate(
        row_number=Window(
            expression=RowNumber(),
            partition_by=[F("title")],
            order_by=[F("title").asc(), F("title")]
        )
    ).filter(row_number=1, longitude__gt=0, latitude__gt=0)
    

    
    # print(media_items.count())
    # print(media_items.values()[1])

    places_data = []
    for item in media_items:
        if item.latitude and item.longitude: # Only include items with location data
            places_data.append({
                'latitude': item.latitude,
                'longitude': item.longitude,
                'timestamp': item.photo_taken_time.isoformat() if item.photo_taken_time else None, # ISO format for JS Date parsing
                'name': item.title if item.title else os.path.basename(item.image.name), # Use title or filename
                'icon': 'camera', # Default icon, can be customized
                'color': 'red',   # Default color, can be customized
                'address': '',    # MediaItem does not have an address field
                'comments': f"User: {item.remarks}",   # MediaItem does not have an comments field
                'image_url': item.image.url, # URL to display image in popup
                'is_video': 1 if (item.title.endswith('.mp4') or item.title.endswith('.MOV')) else 0,
                'is_heic': 1 if (item.title.endswith('.heic') or item.title.endswith('.HEIC')) else 0,
                'people': item.people if item.people else None,
                'url': item.url
            })
    
    # For now, places_by_type will be empty as MediaItem doesn't have a type field
    # If type categorization is needed later, this needs to be extended.
    places_by_type = {}
    
    # TODO: ======================
    """
    for batch in media_items:
        file_type_display = batch.remarks or 'Unknown'
        
        if file_type_display not in places_by_type:
            places_by_type[file_type_display] = {
                'color': BATCH_COLORS.get(batch.remarks, 'blue'),
                'icon': BATCH_ICONS.get(batch.remarks, 'info-circle'),
                'places': []
            }

        for place in media_items:
            places_by_type[file_type_display]['places'].append({
                'name': place.title,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'timestamp': place.photo_taken_time,
            })
            
    """
    # TODO: ======================

    places_json = json.dumps(places_data, cls=DjangoJSONEncoder)
    places_by_type_json = json.dumps(places_by_type, cls=DjangoJSONEncoder)

    context = {
        'places_json': places_json,
        'places_by_type_json': places_by_type_json,
        'is_video': is_video
    }
    return render(request, 'locations/google_photos_map.html', context) # Render map.html instead of takeout.html


class PeopleImages(ListView):
    model = GooglePhotos
    template_name = 'locations/people_images.html'
    context_object_name = "people_images"
    paginate_by = 20


    def get_queryset(self):
        qs = super().get_queryset()
        try:
            person_id = self.request.GET.get("person_id")
            people_name = PeopleNames.objects.get(id=person_id).name
            qs = qs.filter(people__icontains=people_name)
        except:
            people_name = None
            
        try:
            year = int(self.request.GET.get("year"))
            if year>0:
                qs = qs.annotate(
                    photo_year=ExtractYear("photo_taken_time"),
                             ).filter(photo_year=year)
        except:
            year = None
            
        try:
            month = int(self.request.GET.get("month"))
            if month>0:
                qs = qs.annotate(photo_month=ExtractMonth("photo_taken_time")
                             ).filter(photo_month=month)
        except:
            month = None
            
        qs = qs.annotate(
        row_number=Window(
        expression=RowNumber(),
        partition_by=[F("title")],
        order_by=[F("title").asc(), F("title")]
        ),
        person_name= Value(people_name, output_field=CharField()),
        is_location = Case(
        When(longitude__gt=0, then=Value(True)),
        default=Value(False),
        output_field=BooleanField()), # MTS, mp4, 3gp, MOV, MP4, 3GP, MPO, wmv, AVI
        is_video = Case(
        When((Q(title__endswith='.MTS')
             |Q(title__endswith='.mp4')
             |Q(title__endswith='.3gp')
             |Q(title__endswith='.MOV')
             |Q(title__endswith='.MP4')
             |Q(title__endswith='.3GP')
             |Q(title__endswith='.MPO')
             |Q(title__endswith='.wmv')
             |Q(title__endswith='.AVI')
             ),
             then=Value(True)),
        default=Value(False),
        output_field=BooleanField(),
    )).filter(row_number=1).order_by('-photo_taken_time')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_images"] = self.get_queryset().count()
        context["people"] = PeopleNames.objects.all()
        context["years_list"] = GooglePhotos.objects.annotate(year=Substr("photo_taken_time", 1, 4)
                                                        ).values_list("year", flat=True).distinct().order_by("-year")
        return context
