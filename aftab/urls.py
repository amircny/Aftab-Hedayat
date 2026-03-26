from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("accounts.urls")),
    path("events/", include("events.urls")),
    #path("accounts/", include("django.contrib.auth.urls")),

    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change_form.html"
        ),
        name="password_change",
    ),
]