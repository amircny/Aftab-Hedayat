import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", "ADMIN")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
    )
    

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
    

    def __str__(self):
        return self.email
   

class ActivationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="activation")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.token}"

#......................................ActivityLog....................................................
class ActivityLog(models.Model):
        ACTION_CHOICES = [
            ("create_teacher", "Create Teacher"),
            ("edit_teacher", "Edit Teacher"),
            ("delete_teacher", "Delete Teacher"),
            ("create_event", "Create Event"),
            ("edit_event", "Edit Event"),
            ("delete_event", "Delete Event"),
            ("upload_excel", "Upload Excel"),
            ("send_activation_link", "Send Activation Link"),
            ("login", "Login"),
            ("logout", "Logout"),
            ("error", "Error"),
        ]

        STATUS_CHOICES = [
            ("success", "Success"),
            ("warning", "Warning"),
            ("error", "Error"),
        ]

        admin_user = models.ForeignKey(
            "User",
            on_delete=models.CASCADE,
            related_name="activity_logs"
        )
        action = models.CharField(max_length=50, choices=ACTION_CHOICES)
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="success")
        description = models.TextField()
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.admin_user.email} - {self.action} - {self.status}"