from django.shortcuts import render, redirect
from datetime import datetime, date, timedelta
from django.contrib import messages
import os
import math
from django.http import JsonResponse
from django.core.serializers import serialize
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import (Substr, Concat, RowNumber, Replace, Cast, TruncMonth, 
                                        Round, ExtractYear, ExtractMonth, ACos, Cos, Radians, Sin,
                                        Length, LTrim, RTrim, Trim)

from .forms import UrlCreateForm
# ! For GPS ================
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.geos import Point
# from django.contrib.gis.measure import D
# ! For GPS End ================

from django.db.models import F, Q, Case, When, Subquery, OuterRef, Value,CharField, BooleanField, IntegerField, ExpressionWrapper, Window, Count
from .models import LocationBatch, Place, GooglePhotos, PeopleNames, PeopleNamesVideos, LocationAlbumUrls
from .utils import parse_timeline_json, parse_kml, parse_saved_places_json, parse_labeled_places_json
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from py_display import display, CLR
#! display(text, query=False, mysql=False, leading_text="Returned Data 📋", text_clr=CLR.Fg.red, border=True):

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
            media_items = GooglePhotos.objects.filter(Q(image__icontains='.mp4')
                                                      |Q(image__icontains='.mov')
                                                      |Q(image__icontains='.mpo')
                                                      |Q(image__icontains='.wmv')
                                                      |Q(image__icontains='.3gp')
                                                      |Q(image__icontains='.avi')
                                                      |Q(image__icontains='.mts')
                                                      )
    except:
        media_items = GooglePhotos.objects.all()
        is_video = False
        

    media_items = media_items.annotate(
        row_number=Window(
            expression=RowNumber(),
            partition_by=[F("title")],
            order_by=[F("title").asc(), -F("people")]
        )
    ).filter(row_number=1, longitude__gt=0, latitude__gt=0)
    

    
    # print(media_items.count())
    # print(media_items.values()[1])

    target_extensions = ('.mts','.mp4', '.3gp', '.mov', '.mpo', '.wmv', '.avi')
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
                'is_video': 1 if item.title.lower().endswith(target_extensions) else 0,
                'is_heic': 1 if item.title.lower().endswith('.heic') else 0,
                'people': item.people if item.people else None,
                'url': item.url
            })
    # target_extensions = ('.mts', '.3gp', '.mov', '.mpo', '.wmv', '.avi')
    # file.lower().endswith(target_extensions)
    
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
    template_name = 'locations/image_slide_show.html'
    context_object_name = "slides"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()

        try:
            person_id = self.request.GET.get("person_id")
            print(int(person_id))
            if int(person_id) == 10000:
                qs = qs.annotate(
                    people_len=Length(F("people"))
                ).filter(people_len=0)
                people_name = ""
            else:
                people_name = PeopleNames.objects.get(id=person_id).name.lower()
                qs = qs.annotate(
                    person_name=Value(people_name, output_field=CharField())
                ).filter(people__icontains=people_name)
                
        except:
            qs = qs.annotate(
                    people_len=Length(F("people"))
                ).filter(people_len__gt=0)
            people_name = ""
            
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
        partition_by=[F("photo_taken_time")],
        order_by=[F("photo_taken_time").asc(), Length(F("people")).desc(), F("title").desc()]
        ),
        tittle_count=Window(
        expression=Count(F("title")),
        partition_by=[F("title"),F("photo_taken_time")],
        order_by=[F("title").asc(),F("photo_taken_time").asc(), F("people").desc()]
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
        qs = self.get_queryset()
        # display(qs, query=True, mysql=False, leading_text="Query 📋", text_clr=CLR.Fg.red, border=True)
        # display(qs.query)
        try:
            person_name = qs.values()[0]["person_name"].lower()
        except:
            person_name = ""
            
        context = super().get_context_data(**kwargs)
       # ! For pagination -----
       # Get all GET parameters except 'page'
        query_params = self.request.GET.copy()
        # display(query_params)
        if 'page' in query_params:
            del query_params['page']
        
        # If parameters exist, format them as &key=value
        # If they don't exist, this returns an empty string
        context['extra_url_params'] = f"&{query_params.urlencode()}" if query_params else ""
        # ! For pagination end -----
        #! Top 25 ======
        top_25 = PeopleNames.objects.exclude(Q(name__icontains="Jashim Uddin Ahmed") | 
    Q(name__icontains="Shoeb Ahmed Matin")).order_by('-num_of_images')[:13]
        context["top_25"] = top_25
        context["self_url"] = "people_images"
        #! Top 25 end ======
        context["total_images"] = qs.count()
        context["people"] = PeopleNames.objects.all()
        context["heading"] = "Our Friends and Family"
        # context["people_name"] = people_name
        context["years_list"] = GooglePhotos.objects.annotate(
            year=Substr("photo_taken_time", 1, 4)
            ).filter(people__icontains=person_name).values_list("year", flat=True).distinct().order_by("-year")
        return context

    
class PeopleVideos(ListView):
    model = GooglePhotos
    template_name = 'locations/image_slide_show.html'
    context_object_name = "slides"
    paginate_by = 20


    def get_queryset(self):
        qs = super().get_queryset()
        qs= qs.filter((Q(title__endswith='.MTS')
             |Q(title__endswith='.mp4')
             |Q(title__endswith='.3gp')
             |Q(title__endswith='.MOV')
             |Q(title__endswith='.MP4')
             |Q(title__endswith='.3GP')
             |Q(title__endswith='.MPO')
             |Q(title__endswith='.wmv')
             |Q(title__endswith='.AVI')
             ))
        try:
            person_id = self.request.GET.get("person_id")
            if int(person_id) == 10000:
                qs = qs.annotate(
                    people_len=Length(F("people"))
                ).filter(people_len=0)
                people_name = ""
            else:
                people_name = PeopleNamesVideos.objects.get(id=person_id).name.lower()
                qs = qs.filter(people__icontains=people_name)
        except:
            people_name = ""
            
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
                partition_by=[F("photo_taken_time")],
                order_by=[F("photo_taken_time").desc(), Length(F("people")).desc(), F("title").asc(),]
                ),
                person_name= Value(people_name, output_field=CharField()),
                is_location = Case(
                When(longitude__gt=0, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()), # MTS, mp4, 3gp, MOV, MP4, 3GP, MPO, wmv, AVI
                is_video = Value(True, output_field=BooleanField()),
                ).filter(row_number=1).order_by('-photo_taken_time')
        return qs

    def get_context_data(self, **kwargs):
        qs = self.get_queryset()
        try:
            person_name = qs.values()[0]["person_name"].lower()
        except:
            person_name = ""
            
        context = super().get_context_data(**kwargs)
        # ! For pagination -----
       # Get all GET parameters except 'page'
        query_params = self.request.GET.copy()
        # display(query_params)
        if 'page' in query_params:
            del query_params['page']
        
        # If parameters exist, format them as &key=value
        # If they don't exist, this returns an empty string
        context['extra_url_params'] = f"&{query_params.urlencode()}" if query_params else ""
        # ! For pagination end -----
        
        context["total_images"] = qs.count()
        context["people"] = PeopleNamesVideos.objects.all()
        context["heading"] = "Our Friends and Family"
        context["years_list"] = GooglePhotos.objects.filter((Q(title__endswith='.MTS')
             |Q(title__endswith='.mp4')
             |Q(title__endswith='.3gp')
             |Q(title__endswith='.MOV')
             |Q(title__endswith='.MP4')
             |Q(title__endswith='.3GP')
             |Q(title__endswith='.MPO')
             |Q(title__endswith='.wmv')
             |Q(title__endswith='.AVI')
             )).annotate(
                 year=Substr("photo_taken_time", 1, 4)
            ).filter(people__icontains=person_name).values_list("year", flat=True).distinct().order_by("-year")
        return context
    
    
class PeopleVideos_short(ListView):
    model = GooglePhotos
    template_name = 'locations/slideshow_alpine_js.html'
    context_object_name = "slides"
    paginate_by = 20


    def get_queryset(self):
        qs = super().get_queryset()
        qs= qs.filter((Q(title__endswith='.MP4')
             & Q(device_type='IOS_PHONE')
             ))
        try:
            person_id = self.request.GET.get("person_id")
            people_name = PeopleNamesVideos.objects.get(id=person_id).name.lower()
            qs = qs.filter(people__icontains=people_name)
        except:
            people_name = ""
            
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
                partition_by=[F("photo_taken_time")],
                order_by=[F("photo_taken_time").desc(), Length(F("people")).desc(), F("title").asc()]
                ),
                person_name= Value(people_name, output_field=CharField()),
                is_location = Case(
                When(longitude__gt=0, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()), # MTS, mp4, 3gp, MOV, MP4, 3GP, MPO, wmv, AVI
                is_video = Value(True, output_field=BooleanField()),
                ).filter(row_number=1).order_by('-photo_taken_time')
        return qs

    def get_context_data(self, **kwargs):
        qs = self.get_queryset()
        try:
            person_name = qs.values()[0]["person_name"].lower()
        except:
            person_name = ""
            
        context = super().get_context_data(**kwargs)
       # ! For pagination -----
       # Get all GET parameters except 'page'
        query_params = self.request.GET.copy()
        # display(query_params)
        if 'page' in query_params:
            del query_params['page']
        
        # If parameters exist, format them as &key=value
        # If they don't exist, this returns an empty string
        context['extra_url_params'] = f"&{query_params.urlencode()}" if query_params else ""
        # ! For pagination end -----
        
        context["total_images"] = qs.count()
        context["heading"] = "Our Friends and Family"
        context["people"] = PeopleNamesVideos.objects.all()
        context["years_list"] = GooglePhotos.objects.filter((Q(title__endswith='.MP4')
             & Q(device_type='IOS_PHONE')
             )).annotate(
                 year=Substr("photo_taken_time", 1, 4)
            ).filter(people__icontains=person_name).values_list("year", flat=True).distinct().order_by("-year")
        return context
    
    
class SlideShowView(ListView):
    model = GooglePhotos
    template_name = 'locations/slideshow_alpine_js.html'
    context_object_name = 'slides'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()

        try:
            person_id = self.request.GET.get("person_id")
            # print(int(person_id))
            if int(person_id) == 10000:
                qs = qs.annotate(
                    people_len=Length(F("people"))
                ).filter(people_len=0)
                people_name = ""
            else:
                people_name = PeopleNames.objects.get(id=person_id).name.lower()
                qs = qs.annotate(
                    person_name=Value(people_name, output_field=CharField())
                ).filter(people__icontains=people_name)
                
        except:
            qs = qs.annotate(
                    people_len=Length(F("people"))
                ).filter(people_len__gt=0)
            people_name = ""
            
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
        partition_by=[F("photo_taken_time")],
        order_by=[F("photo_taken_time").desc(), Length(F("people")).desc(), F("title").asc()]
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
        qs = self.get_queryset()
        try:
            person_name = qs.values()[0]["person_name"].lower()
        except:
            person_name = ""
            
        context = super().get_context_data(**kwargs)
       # ! For pagination -----
       # Get all GET parameters except 'page'
        query_params = self.request.GET.copy()
        # display(query_params)
        if 'page' in query_params:
            del query_params['page']
        
        # If parameters exist, format them as &key=value
        # If they don't exist, this returns an empty string
        context['extra_url_params'] = f"&{query_params.urlencode()}" if query_params else ""
        # ! For pagination end -----
                #! Top 25 ======
        top_25 = PeopleNames.objects.exclude(Q(name__icontains="Jashim Uddin Ahmed") | 
    Q(name__icontains="Shoeb Ahmed Matin")).order_by('-num_of_images')[:13]
        context["top_25"] = top_25
        context["self_url"] = "slides"
        #! Top 25 end ======
        context["total_images"] = qs.count()
        context["people"] = PeopleNames.objects.all()
        context["heading"] = "Our Friends and Family"
        # context["people_name"] = people_name
        context["years_list"] = GooglePhotos.objects.annotate(
            year=Substr("photo_taken_time", 1, 4)
            ).filter(people__icontains=person_name).values_list("year", flat=True).distinct().order_by("-year")
        return context


from django.shortcuts import get_object_or_404
from django.http import HttpResponse

def download_media(request, media_id):
    media_item = get_object_or_404(GooglePhotos, pk=media_id)
    
    # Get the file path from the image field
    file_path = media_item.image.path
    
    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        # Create an HttpResponse with the file content
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        
        # Set the Content-Disposition header to prompt a download
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        
        return response


class ImageWithDescription(ListView):
    model = GooglePhotos
    template_name = 'locations/slideshow_alpine_js.html'
    context_object_name = "slides"
    paginate_by = 75


    def get_queryset(self):
        qs = super().get_queryset()
        try:
            person_id = self.request.GET.get("person_id")
            print(int(person_id))
            if int(person_id) == 10000:
                qs = qs.annotate(
                    people_len=Length(F("people"))
                ).filter(people_len=0)
                people_name = ""
            else:
                people_name = PeopleNames.objects.get(id=person_id).name.lower()
                qs = qs.annotate(
                    person_name=Value(people_name, output_field=CharField())
                ).filter(people__icontains=people_name)
                
        except:
            qs = qs.annotate(
                    people_len=Length(F("people"))
                ).filter(people_len__gt=0)
            people_name = ""
            
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
        description_len=Length(Trim(F("description"))),
        row_number = Window(
        expression=RowNumber(),
        partition_by=[F("photo_taken_time")],
        order_by=[F("photo_taken_time").asc(), Trim(F("description")).desc()]
        ),
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
    )).filter(Q(description_len__gt=1)
              & Q(row_number=1)
            #   & Q(Q(title__icontains='Morjina') | Q(title__icontains='AAAA0033.JPG')| Q(title__icontains='AAAA0034.JPG'))
              )
        qs = qs.annotate(
            image_num=Window(
                expression=Count(F("description"),),
                partition_by=[F("description")],
                order_by=F("description").desc()
            )
        ).order_by('-image_num','-photo_taken_time')
        # print(qs.values()[0])
        return qs

    def get_context_data(self, **kwargs):
        qs = self.get_queryset()
        # display(qs, query=True, mysql=False, leading_text="Query 📋", text_clr=CLR.Fg.red, border=True)
        # display(qs.query)
        try:
            person_name = qs.values()[0]["person_name"].lower()
        except:
            person_name = ""
            
        context = super().get_context_data(**kwargs)
        people = [name.strip().lower() 
               for people_names in GooglePhotos.objects.annotate(
               ).filter(description__icontains="ICM107B").values_list("people", flat=True).distinct()
               for name in people_names.split(",")]
        people = list(set(people))
        # flat_result = [item for sublist in people for item in sublist]
        # print(flat_result)
        people = PeopleNames.objects.filter(name__in=people)
        context["heading"] = "My First Digital Camera"
        context["people"] = people
       # ! For pagination -----
       # Get all GET parameters except 'page'
        query_params = self.request.GET.copy()
        # display(query_params)
        if 'page' in query_params:
            del query_params['page']
        
        # If parameters exist, format them as &key=value
        # If they don't exist, this returns an empty string
        context['extra_url_params'] = f"&{query_params.urlencode()}" if query_params else ""
        # ! For pagination end -----
        #! Top 25 ======
        top_25 = people.exclude(Q(name__icontains="Jashim Uddin Ahmed") | 
        Q(name__icontains="Shoeb Ahmed Matin")).order_by('-num_of_images')[:10]
        context["top_25"] = top_25
        context["self_url"] = "image_with_description"
        #! Top 25 end ======
        context["total_images"] = qs.count()
        context["total_first_digital_cam"]=qs.filter(description__icontains="ICM107B").count()
        context["total_others"]=qs.exclude(description__icontains="ICM107B").count()
        # people = [people_names.split(",") for people_names in qs.values_list("people", flat=True).distinct()]
        
        # context["people_name"] = people_name
        context["years_list"] = GooglePhotos.objects.annotate(
            year=Substr("photo_taken_time", 1, 4)
            ).filter(people__icontains=person_name).values_list("year", flat=True).distinct().order_by("-year")
        return context


class LocationAlbum(ListView):
    model = GooglePhotos
    template_name = 'locations/location_album.html'
    context_object_name = "slides"
    paginate_by = 50

    def get_queryset(self):
        video_exts = ['mts', 'mp4', '3gp', 'mov', 'mpo', 'wmv', 'avi']

        qs = super().get_queryset().annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("title")],
                order_by=[F("title").asc(), Trim(F("photo_taken_time")).desc()]
            ),
            is_location=Case(
                When(longitude__gt=0, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            is_video = Case(
                When(title__iregex=r'\.({})$'.format('|'.join(video_exts)), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).filter(row_number=1).exclude(local_folder__icontains="WhatsApp")

        try:
            url_id = int(self.request.GET.get("url_id"))
            image_type = int(self.request.GET.get("image_type"))
            url_data = LocationAlbumUrls.objects.get(id=url_id)
        except LocationAlbumUrls.DoesNotExist:
            url_data = None

        center_lat = getattr(url_data, "center_lat", 0)
        center_lng = getattr(url_data, "center_lng", 0)
        radius_km = getattr(url_data, "radius_km", 2)
        page_header_text = getattr(url_data, "page_header_text", "Tour Albums")

        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * math.cos(math.radians(center_lat)))

        results = qs.filter(
            latitude__range=(center_lat - lat_delta, center_lat + lat_delta),
            longitude__range=(center_lng - lng_delta, center_lng + lng_delta)
        ).annotate(
            month_group=TruncMonth('photo_taken_time'),
            distance=6371 * ACos(
                Cos(Radians(center_lat)) * Cos(Radians(F('latitude'))) *
                Cos(Radians(F('longitude')) - Radians(center_lng)) +
                Sin(Radians(center_lat)) * Sin(Radians(F('latitude')))
            ),
            page_header_text=Value(page_header_text, output_field=CharField()),
            people_len=Length(Trim(F("people"))),
        )
        if image_type==1:
            results = results.filter(distance__lte=radius_km).order_by('-photo_taken_time')
        elif image_type==2:
            results = results.filter(distance__lte=radius_km, people_len__gt=0).order_by('-photo_taken_time')
        else:
            results = results.filter(distance__lte=radius_km, people_len__lt=1).order_by('-photo_taken_time')
            
        return results

    def get_context_data(self, **kwargs):
        qs = self.get_queryset()
        # qs = data["results"]
        # url_data = data["url_data"]
        # heading_list = ["Sreemangal Tour Album", "Vietnam Tour Album", "Madinah, Saudi Arabia", "Makkah, Saudi Arabia"]
        context = super().get_context_data(**kwargs)
        # display(qs.values()[0]["page_header_text"])
        # data = self.get_queryset()
        # context.update({
        #     "results": data["results"],
        #     "url_data": data["url_data"],
        # })
        try:
            context["heading"] = qs.values()[0]["page_header_text"]
        except:
            context["heading"] = "Tour Albums"
       # ! For pagination -----
       # Get all GET parameters except 'page'
        query_params = self.request.GET.copy()
        # print(query_params)
        # display(query_params)
        if 'page' in query_params:
            del query_params['page']
        
        # If parameters exist, format them as &key=value
        # If they don't exist, this returns an empty string
        context['extra_url_params'] = f"&{query_params.urlencode()}" if query_params else ""
        # ! For pagination end -----
        context["self_url"] = "location_album"
        context["total_images"] = qs.count()
        return context

def location_album_urls(request):
    # ?center_lat=24.312077&center_lng=91.727410&radius_km=12 21.422513, 39.826196
    urls_list = LocationAlbumUrls.objects.all()
    return render(request, 'locations/location_url_list.html', {'urls_list': urls_list,"heading": "Tour Albums"})

# Region
# import math
# from django.db.models import F, FloatField
# from django.db.models.functions import ACos, Cos, Radians, Sin

# def get_nearby_data(center_lat, center_lng, radius_km=2):
#     # 1. Calculate Bounding Box (Pruning)
#     # 1 degree of Lat is ~111km
#     lat_delta = radius_km / 111.0
#     # 1 degree of Lng varies based on Latitude
#     lng_delta = radius_km / (111.0 * math.cos(math.radians(center_lat)))

#     # 2. Query with Bounding Box + Haversine Annotation
#     return YourModel.objects.filter(
#         latitude__range=(center_lat - lat_delta, center_lat + lat_delta),
#         longitude__range=(center_lng - lng_delta, center_lng + lng_delta)
#     ).annotate(
#         distance=(
#             6371 * ACos(
#                 Cos(Radians(center_lat)) * Cos(Radians(F('latitude'))) *
#                 Cos(Radians(F('longitude')) - Radians(center_lng)) +
#                 Sin(Radians(center_lat)) * Sin(Radians(F('latitude')))
#             )
#         )
#     ).filter(distance__lte=radius_km).order_by('distance')

# class LocationAlbum_2(ListView):
#     model = LocationBatch
#     template_name = 'locations/location_album.html'
#     context_object_name = "location_album"
#     paginate_by = 500

#     def get_queryset(self):
#         qs = super().get_queryset()
#         try:
#             center_lat = self.request.GET.get("center_lat")
#             center_lng = self.request.GET.get("center_lng")
#             distance = self.request.GET.get("distance")
#         except:
#             center_lat =0
#             center_lng =0
#         center = Point(center_lng, center_lat, srid=4326)

#         # This is extremely fast and handles all the math for you
#         results = qs.filter(
#             location__distance_lte=(center, D(km=distance))
#         ).annotate(distance=Distance('location', center)).order_by('distance')            

#         return results
# Endregion

class UrlCreateView(CreateView):
    template_name = "locations/location_url_add.html"
    form_class = UrlCreateForm
    success_url = "./"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["urls_list"] = LocationAlbumUrls.objects.all()
        context["heading"] = "Add New URL for Tour Albums"
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thank you. A new URL has been created.")
        return super(UrlCreateView, self).form_valid(form)
    

class UrlUpdateView(UpdateView):
    model = LocationAlbumUrls
    form_class = UrlCreateForm
    template_name = "locations/location_url_add.html"
    success_url = "/location_album_urls/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["heading"] = "Location Album URL Update"
        context["update_tag"] = True
        context["redirect_url"] = f"./{self.kwargs['pk']}"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, "The URL's information updated successfully."
        )
        return super(UrlUpdateView, self).form_valid(form)