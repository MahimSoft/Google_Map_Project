from django.shortcuts import render, redirect
from datetime import datetime, date, timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import Substr, Concat, RowNumber, Replace, Cast, TruncMonth, Round
from django.db.models import F, Q, Subquery, OuterRef, Value, IntegerField, ExpressionWrapper, Window
from .models import Timeline
from .forms import YearMonthForm
from py_display import *


def time_line_view(request):
    try:
        given_year_month = int(f"{request.GET['year']}{request.GET['month']}")
        given_date = f"{request.GET['year']}-{request.GET['month']}-01"
        display_month = datetime.strptime(given_date, "%Y-%m-%d").strftime("%B %Y")

    except:
        given_year_month = 202405
        given_date = date(2024,5,1)
        display_month = given_date.strftime("%B %Y")
        
    # xx = Timeline.objects.annotate(
    # TruncMonth = TruncMonth("date_time_extracted")
    # ).filter(
    #     TruncMonth = given_date
    # )
        
    # print("📌📌: ",xx[0], xx.explain())
        
    # print(f"🔖: {year_month}")
    qs = Timeline.objects.filter(
        year_month = given_year_month
    ).annotate(
        hour_key=Substr("date_time_extracted", 1, 13),
        truncmonth = TruncMonth("date_time_extracted"),
        date_int=Cast(
        Replace(
            Replace(F("hour_key"), Value("-"), Value("")),
            Value(" "), Value("")
        ),
        IntegerField()
        ),
        row_number=Window(
            expression=RowNumber(),
            partition_by=[F("date_int")],
            order_by=[F("date_int").asc(), F("accuracy").asc()]
        )
    ).filter(row_number=1)
    
    
    # print(f"🔖: {qs[0].truncmonth} - {qs[0].date_time_extracted}-{qs[0]}")
    
    qs = qs.annotate(
        dt_n_point = ExpressionWrapper(
             F("date_int")/100, output_field=IntegerField()
        ),
        row_number_1=Window(
        expression=RowNumber(),
        # Concat('first_name', Value(' '), 'last_name', output_field=CharField())
        partition_by=[F("dt_n_point"), Concat(Round(F("latitude"), 3) , Round(F("longitude"), 3), F("accuracy"))],
        order_by=[F("dt_n_point").asc(), Concat(Round(F("latitude"), 3) , Round(F("longitude"),3), F("accuracy")).asc()]
        )
    ).filter(row_number_1=1)
    
    # print(f"🔖: {qs.query}")
    
    # return render(request, 'maps/test.html',{'context':qs, 'form':YearMonthForm})
    file_type_display = "Timeline"
    places_by_type = {}
        
    places_by_type[file_type_display] = {
        'color':  'blue',
        'icon':'info-circle',
        'places': []
    }

    for place in qs:
        places_by_type[file_type_display]['places'].append({
            'name': place.date_time_extracted.strftime("%d %B, %Y: %H:%M"),
            'latitude': place.latitude,
            'longitude': place.longitude,
            'address': "Address",
            'timestamp': place.date_time_extracted,
        })
        
    flat_places_list = []
    for place in qs:
        # for place in batch:
        flat_places_list.append({
            'name': place.date_time_extracted.strftime("%d %B, %Y: %H:%M"),
            'latitude': place.latitude,
            'longitude': place.longitude,
            'address': "Address",
            'timestamp': place.date_time_extracted,
            'color': 'blue',
            'icon': 'info-circle'
        })
        
        display(qs, query=True)
        
    return render(request, 'timeline/timeline.html', {
        'places_by_type_json': json.dumps(places_by_type, cls=DjangoJSONEncoder),
        'places_json': json.dumps(flat_places_list, cls=DjangoJSONEncoder),
        'form':YearMonthForm,
        'display_month': display_month
    })

