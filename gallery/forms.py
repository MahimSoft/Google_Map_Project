from django import forms

class MediaItemForm(forms.Form):
    image = forms.FileField(widget=forms.FileInput())
