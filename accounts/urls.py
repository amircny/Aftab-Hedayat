from django.urls import path
from . import views

app_name = "accounts"   # ⭐ خیلی مهم برای reverse و namespace

urlpatterns = [

    # 🔐 Auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ⭐ Activation (Teacher Account)
    path(
        "activate/<uuid:token>/",
        views.activate_account,
        name="accounts_activate",
    ),

    # 🎓 Teacher Dashboard
    path(
        "dashboard/",
        views.teacher_dashboard,
        name="teacher_dashboard",
    ),

    # 👑 Admin Dashboard
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),
    # Delete AdminDashbord Teacher
    path(
        "teachers/delete/<int:teacher_id>/",
          views.delete_teacher, name="delete_teacher"
        ),
    #Edit Admind Dashbord Teacher
    path(
        "teachers/edit/<int:teacher_id>/", 
        views.edit_teacher, name="edit_teacher"
        ),
]