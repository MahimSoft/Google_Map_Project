
#! Command: python manage.py inspectdb --database=timeline_db > .\timeline\models.py

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models import CharField
from django.db.models.functions import Cast, Left, TruncMonth

class Timeline(models.Model):
    latitudeE7 =  models.CharField(max_length=255, blank=True, null=True)
    longitudeE7 =  models.CharField(max_length=255, blank=True, null=True)
    accuracy =  models.IntegerField("Accuracy", default=0, blank=True, null=True)
    source =  models.CharField(max_length=255, blank=True, null=True)
    timestamp =  models.CharField(max_length=255, blank=True, null=True)
    date_time_extracted =  models.DateTimeField(blank=True, null=True)
    year_month =  models.IntegerField("Month", default=0, blank=True, null=True, db_index=True)
    deviceDesignation =  models.CharField(max_length=255, blank=True, null=True)
    activity =  models.CharField(max_length=255, blank=True, null=True)
    deviceTag =  models.CharField(max_length=255, blank=True, null=True)
    altitude =  models.CharField(max_length=255, blank=True, null=True)
    verticalAccuracy =  models.CharField(max_length=255, blank=True, null=True)
    platformType =  models.CharField(max_length=255, blank=True, null=True)
    serverTimestamp =  models.CharField(max_length=255, blank=True, null=True)
    deviceTimestamp =  models.CharField(max_length=255, blank=True, null=True)
    batteryCharging =  models.CharField(max_length=255, blank=True, null=True)
    formFactor =  models.CharField(max_length=255, blank=True, null=True)
    velocity =  models.CharField(max_length=255, blank=True, null=True)
    heading =  models.CharField(max_length=255, blank=True, null=True)
    osLevel =  models.CharField(max_length=255, blank=True, null=True)
    locationMetadata =  models.CharField(max_length=255, blank=True, null=True)
    inferredLocation =  models.CharField(max_length=255, blank=True, null=True)
    placeId =  models.CharField(max_length=255, blank=True, null=True)
    activeWifiScan =  models.CharField(max_length=255, blank=True, null=True)
    latitude =  models.FloatField()
    longitude =  models.FloatField()
    
    class Meta:
        managed = False
        db_table = 'maps_timeline'
        indexes = [
            models.Index(fields=["date_time_extracted", "accuracy"]),
            models.Index(fields=["latitude", "longitude"]),
            models.Index(
            Left(Cast('date_time_extracted', CharField()), 7), 
            name='date_time_extracted_str_7_idx'
        ),
        ]

    def __str__(self):
        # return self.name or f"Point at {self.latitude}, {self.longitude}"
        return f"Point at {self.latitude}, {self.longitude}, Date Time: {self.timestamp}"
