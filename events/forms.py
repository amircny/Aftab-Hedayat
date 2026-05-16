from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['available_from'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['available_until'].input_formats = ['%Y-%m-%dT%H:%M']
    class Meta:
        model = Event
        fields = [
            "title",
            "event_date",
            "event_time",
            "meeting_link",
            "available_from",
            "available_until",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "عنوان کلاس یا رویداد"}),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "event_time": forms.TimeInput(attrs={"type": "time"}),
            "meeting_link": forms.URLInput(attrs={"placeholder": "لینک Google Meet"}),
            "available_from": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M"
            ),
            "available_until": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M"
            ),
        }


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label="فایل اکسل")