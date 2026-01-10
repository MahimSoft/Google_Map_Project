from django import forms
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models.functions import Substr
from .models import Timeline

# def get_year_choices():
#     # format_string = '%Y-%m-%dT%H:%M:%S.%f'
#     years = Timeline.objects.annotate(
#         year=ExtractYear(Substr("timestamp", 1, 4))
#     ).values_list("year", flat=True).distinct().order_by("year")
#     return [(y, y) for y in years]

# def get_month_choices():
#     months = Timeline.objects.annotate(
#         month=ExtractMonth("timestamp")
#     ).values_list("month", flat=True).distinct().order_by("month")
#     return [(m, m) for m in months]

class YearMonthForm(forms.Form):
    year = forms.ChoiceField(choices=[], label="Year: ")
    month = forms.ChoiceField(choices=[], label="Month: ")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].choices = [
            (y, y) for y in Timeline.objects
                .annotate(year=Substr("timestamp", 1, 4))
                .values_list("year", flat=True).distinct().order_by("year")
        ]
        self.fields["month"].choices = [
            (m, m) for m in Timeline.objects
                .annotate(month=Substr("timestamp", 6, 2))
                .values_list("month", flat=True).distinct().order_by("month")
        ]

# class YearMonthForm(forms.Form):
#     year = forms.ChoiceField(choices=[], label="Year")
#     month = forms.ChoiceField(choices=[], label="Month")

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["year"].choices = get_year_choices()
#         self.fields["month"].choices = get_month_choices()