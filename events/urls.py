from django.urls import path
from . import views
from .views import check_student_access
from .views import export_attendance
urlpatterns = [
    path("", views.teacher_dashboard, name="teacher_dashboard"),
    path("create/", views.create_event, name="create_event"),
    path("upload-excel/<int:event_id>/", views.upload_student_excel, name="upload_student_excel"),
    path("delete/<int:event_id>/", views.delete_event, name="delete_event"),
    path("report/<int:event_id>/", views.event_report, name="event_report"),
    path("check-access/", check_student_access),
    path("export-attendance/<int:event_id>/", export_attendance),
    path("edit/<int:event_id>/", views.edit_event, name="edit_event"),
]


