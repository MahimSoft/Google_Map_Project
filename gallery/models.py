from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import extract_photo_metadata

class MediaItem(models.Model):
    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='takeout_media/')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    is_video = models.BooleanField(default=False)

    def __str__(self):
        return self.title or f"Media {self.id}"
    

class Photo(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='photos/')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    captured_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title or f"Photo {self.id}"
    
    
# models.py (continued)

            
@receiver(post_save, sender=Photo)
def process_photo_metadata(sender, instance, created, **kwargs):
    if created and instance.image:
        lat, lon, dt = extract_photo_metadata(instance.image.path)
        
        # Using .update() prevents the signal from firing again in an infinite loop
        Photo.objects.filter(id=instance.id).update(
            latitude=lat, 
            longitude=lon, 
            captured_at=dt
        )