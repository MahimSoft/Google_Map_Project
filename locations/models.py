from django.db import models
import os
from uuid import uuid4
from django.db.models.functions import Cast, Left, TruncMonth
from django.db.models import CharField

def path_and_rename_logo(instance, filename, upload_folder = "images"):
    upload_to = upload_folder
    ext = filename.split(".")[-1]
    if ext.lower() != "svg":
        ext = "webp"

    if instance.pk:
        filename = "{}_{}.{}".format(instance.pk, uuid4().hex, ext)
    else:
        # set filename as random string
        filename = "{}.{}".format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

class LocationBatch(models.Model):
    """Represents a single file upload (e.g., 'Jan 2024 Timeline' or 'Japan Trip MyMap')"""
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50, choices=[
        ('timeline', 'Google Timeline (JSON)'),
        ('mymaps', 'My Maps (KML/KMZ)'),
        ('saved', 'Saved Places (JSON)'),
        ('labeled', 'Labeled Places (JSON)')
    ])
    color = models.CharField(max_length=7, default='#3498db') # Default to a nice blue

    def __str__(self):
        return f"{self.name} ({self.file_type})"

class Place(models.Model):
    """A specific point on the map"""
    batch = models.ForeignKey(LocationBatch, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    place_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timeline specific fields
    confidence = models.IntegerField(null=True, blank=True) # Google's confidence in the visit
    duration_start = models.DateTimeField(null=True, blank=True)
    duration_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name or f"Point at {self.latitude}, {self.longitude}"


class GooglePhotos(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image_views = models.IntegerField(default=0)
    creation_time = models.DateTimeField(null=True, blank=True)
    photo_taken_time = models.DateTimeField(null=True, blank=True, db_index=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    people = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    image = models.ImageField(
        upload_to = path_and_rename_logo,
        max_length=255,
        # validators=[validate_file_extension],
        # default="ContractorsImage/default.png",
        null=True,
        blank=True,
    )
    video_thumbnail = models.ImageField(
        upload_to = 'thumbnails',
        max_length=255,
        # validators=[validate_file_extension],
        # default="ContractorsImage/default.png",
        null=True,
        blank=True,
    )
    url = models.URLField(max_length=500, blank=True, null=True)
    local_folder = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.title}, {self.photo_taken_time or ''}"
    

class PeopleNames(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    num_of_images = models.IntegerField(null=True, blank=True) # Google's confidence in the visit
    
    def __str__(self):
        return f"{self.name}"
    
class PeopleNamesVideos(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    num_of_videos = models.IntegerField(null=True, blank=True) # Google's confidence in the visit
    
    def __str__(self):
        return f"{self.name}"