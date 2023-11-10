# media_references/forms.py
from django import forms
from .models import *

class MediaReferenceForm(forms.ModelForm):
    class Meta:
        model = MediaReference
        fields = ['reference_link']

MediaReferenceFormSet = forms.formset_factory(
    MediaReferenceForm,
    extra=1,
    can_delete=True,
)


class ImageForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['cover_image']