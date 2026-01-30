from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Reset, HTML
from .models import LocationAlbumUrls

class UrlCreateForm(forms.ModelForm):
    class Meta:
        model = LocationAlbumUrls
        fields = "__all__"
        labels = {
            "center_lat": "Latitude",
            "center_lng": "Longitude",
            "radius_km": "Radius (km)",
            "url_display_text": "URL Display Text",
            "page_header_text": "Page Title",
            "thumbnail": "Url Thumbnail",
            "image_type": "Default Image Type",
        }
        widgets = {
            "thumbnail": forms.FileInput(),
            "image_type": forms.RadioSelect(),   # 👈 force radio buttons
        }

    def __init__(self, *args, **kwargs):
        super(UrlCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.attrs["autocomplete"] = "off"
        self.helper.layout = Layout(
            Row(
                Column("image_type", css_class="flex justify-between space-x-2 item-center"),
                css_class="flex justify-between space-x-2 item-center space-x-2",
            ),
            Row(
                Column("center_lat", css_class="flex flex-col w-2/12 mb-0 mr-2"),
                Column("center_lng", css_class="flex flex-col w-2/12 mb-0 mx-2"),
                Column("radius_km", css_class="flex flex-col w-2/12 mb-0 mx-4"),
                Column("url_display_text", css_class="flex flex-col w-3/12 mb-0 mr-2"),
                Column("page_header_text", css_class="flex flex-col w-3/12 mb-0 mr-2"),
                css_class="flex flex-row space-x-2",
            ),
            Row(
                HTML("<div class='flex flex-col mb-1 mr-2 flex-wrap flex-row space-x-2'>"),
                HTML("""<img class='border-1 rounded-md ml-4' id='blah' src='{{object.thumbnail_url}}' onerror="this.src='/static/images/096.png'" alt='' width='100' height='100'/>"""),
                Column("thumbnail", css_class="flex flex-col mb-0 mr-2"),
                HTML("</div>"),
                HTML("<div class='flex justify-end mb-1 mr-2' id ='button_div'>"),
                Submit("submit", "Submit", css_class="btn btn-success btn-sm me-2 mb-0"),
                Reset("reset", "Reset", css_class="btn btn-danger btn-sm me-2 mb-0"),
                HTML("<a href='{{ request.META.HTTP_REFERER }}' class='btn btn-primary btn-sm me-0 mb-0' role='button'><i class='bi bi-arrow-left-square'></i> Back</a>"),
                HTML("</div>"),
                css_class="flex justify-between flex-row space-x-2",
            )
        )