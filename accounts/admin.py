from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User
from django.urls import reverse
from django.utils.html import format_html
from .models import ActivationToken
from django.core.mail import send_mail
from django.conf import settings 

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ("email",)
    list_display = ("email", "role", "is_verified", "is_active", "is_staff")
    list_filter = ("role", "is_verified", "is_active", "is_staff")

    fieldsets = (
        (None, {"fields": ("email", "password", "role", "is_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "role", "password1", "password2", "is_active", "is_verified", "is_staff"),
        }),
    )
    def activation_link(self, obj):
     if obj.role != "TEACHER":
        return "-"
     token_obj = ActivationToken.objects.filter(user=obj).first()
     if not token_obj:
         return "No token"
     url = reverse("accounts_activate", args=[str(token_obj.token)])
     return format_html('<a href="{}" target="_blank">Open activation link</a>', url)
    
    def save_model(self, request, obj, form, change):
     is_new_teacher = not change and obj.role == "TEACHER"

     super().save_model(request, obj, form, change)

     if is_new_teacher:
        token = ActivationToken.objects.create(user=obj)

        activation_url = request.build_absolute_uri(
            reverse("accounts_activate", args=[str(token.token)])
        )

        send_mail(
            subject="Activate your account",
            message=f"Click this link to activate your account:\n\n{activation_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[obj.email],
        )

    list_display = ("email", "role", "is_verified", "is_active", "is_staff", "activation_link")
    readonly_fields = ("activation_link",)
    search_fields = ("email",)
    filter_horizontal = ("groups", "user_permissions")