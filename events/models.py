from django.db import models
from django.conf import settings


class Event(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
        limit_choices_to={"role": "TEACHER"},
    )
    title = models.CharField(max_length=200)
    meeting_link = models.URLField()
    event_date = models.DateField()
    event_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AllowedStudent(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="allowed_students",
    )
    student_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.student_id} - {self.event.title}"