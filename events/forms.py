from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "event_date", "event_time", "meeting_link"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "عنوان کلاس یا رویداد"}),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "event_time": forms.TimeInput(attrs={"type": "time"}),
            "meeting_link": forms.URLInput(attrs={"placeholder": "لینک Google Meet"}),
        }


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label="فایل اکسل")