from django.contrib import admin
from .models import Event, AllowedStudent


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher")
    search_fields = ("title",)


admin.site.register(AllowedStudent)