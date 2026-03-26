from django.urls import path
from . import views

urlpatterns = [
    path("", views.teacher_dashboard, name="teacher_dashboard"),
    path("create/", views.create_event, name="create_event"),
    path("upload-excel/<int:event_id>/", views.upload_student_excel, name="upload_student_excel"),
    path("delete/<int:event_id>/", views.delete_event, name="delete_event"),
    path("report/<int:event_id>/", views.event_report, name="event_report"),
]