from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.crypto import get_random_string
from events.forms import EventForm
from events.models import Event
from .forms import EmailLoginForm
from .models import ActivationToken
from .models import User
from .forms import TeacherEditForm
from django.http import JsonResponse
from .models import ActivationToken, ActivityLog
from django.contrib.auth.hashers import make_password

User = get_user_model()


def is_admin(user):
    return user.is_authenticated and user.is_superuser


def activate_account(request, token):
    activation = get_object_or_404(ActivationToken, token=token)
    user = activation.user

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.is_verified = True
            user.is_active = True
            user.save()
            activation.delete()
            return redirect("accounts:login")
    else:
        form = SetPasswordForm(user)

    return render(request, "accounts/activate.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = EmailLoginForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            if user.is_superuser:
                return redirect("accounts:admin_dashboard")
            else:
                return redirect("accounts:teacher_dashboard")
    else:
        form = EmailLoginForm()

    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def teacher_dashboard(request):
    events = Event.objects.filter(teacher=request.user)
    form = EventForm()

    return render(
        request,
        "accounts/dashboard.html",
        {
            "events": events,
            "form": form,
        },
    )


@login_required
@user_passes_test(is_admin)
#............................Delete Teacher adminpanel...................................
def delete_teacher(request, teacher_id):
    if request.method != "POST":
        return redirect("accounts:admin_dashboard")

    teacher = get_object_or_404(User, id=teacher_id, role="TEACHER")
    ActivityLog.objects.create(
        admin_user=request.user,
        action="create_teacher",
        status="success",
        description=f"استاد جدید با ایمیل {teacher.email} ایجاد شد."
    )
    teacher.delete()
    return redirect("accounts:admin_dashboard")
#...........................reset_teacher_password.........................................
def reset_teacher_password(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id, role="TEACHER")

    if request.method == "POST":
        new_password = request.POST.get("new_password", "").strip()

        if not new_password:
            return JsonResponse({"success": False, "message": "رمز جدید وارد نشده است."}, status=400)

        teacher.password = make_password(new_password)
        teacher.save()

        ActivityLog.objects.create(
            admin_user=request.user,
            action="edit_teacher",
            status="success",
            description=f"رمز عبور استاد {teacher.email} توسط ادمین بازنشانی شد."
        )

        return JsonResponse({"success": True, "message": "رمز عبور استاد با موفقیت تغییر کرد."})

    return JsonResponse({"success": False, "message": "رمز جدید وارد نشده است."}, status=400)
#.......................................................................................
def admin_dashboard(request):
    teachers = User.objects.filter(role="TEACHER")

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    sort = request.GET.get("sort", "").strip()

    if search:
        teachers = teachers.filter(email__icontains=search) | User.objects.filter(role="TEACHER", first_name__icontains=search) | User.objects.filter(role="TEACHER", last_name__icontains=search)

    if status == "active":
        teachers = teachers.filter(is_active=True, is_verified=True)
    elif status == "pending":
        teachers = teachers.filter(is_active=False, is_verified=False)

    if sort == "name":
        teachers = teachers.order_by("first_name", "last_name")
    else:
        teachers = teachers.order_by("-date_joined")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        if not first_name or not last_name or not email:
            return render(
                request,
                "accounts/admin_dashboard.html",
                {
                    "teachers": teachers,
                    "error": "لطفاً همه فیلدها را کامل کنید.",
                },
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "accounts/admin_dashboard.html",
                {
                    "teachers": teachers,
                    "error": "این ایمیل قبلاً ثبت شده است.",
                },
            )

        teacher = User.objects.create_user(
            email=email,
            password=get_random_string(12),
            first_name=first_name,
            last_name=last_name,
            role="TEACHER",
            is_active=False,
            is_verified=False,
        )
        #.......................................................................................................
        ActivityLog.objects.create(
            admin_user=request.user,
            action="create_teacher",
            status="success",
            description=f"استاد جدید با ایمیل {teacher.email} ایجاد شد."
        )
        #.......................................................................................................
        activation = ActivationToken.objects.create(user=teacher)

        activation_url = request.build_absolute_uri(
            reverse("accounts:accounts_activate", args=[str(activation.token)])
        )

        send_mail(
            subject="Activate your account",
            message=f"Click this link to activate your account:\n\n{activation_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[teacher.email],
            fail_silently=False,
        )

        print("ACTIVATION LINK:", activation_url)

        teachers = User.objects.filter(role="TEACHER").order_by("-date_joined")
        return render(
            request,
            "accounts/admin_dashboard.html",
            {
                "teachers": teachers,
                "success": "استاد با موفقیت ثبت شد و لینک فعال‌سازی ارسال شد.",
                "activation_url": activation_url,
            },
        )

    return render(
        request,
        "accounts/admin_dashboard.html",
        {
            "teachers": teachers,
        },
    )
#............................Edit Teacher ...................................
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id, role="TEACHER")

    if request.method == "POST":
        teacher.first_name = request.POST.get("first_name", "").strip()
        teacher.last_name = request.POST.get("last_name", "").strip()
        teacher.email = request.POST.get("email", "").strip()
        teacher.save()
        ActivityLog.objects.create(
            admin_user=request.user,
            action="edit_teacher",
            status="success",
            description=f"اطلاعات استاد {teacher.email} ویرایش شد."
        )
        return JsonResponse({"success": True, "message": "اطلاعات استاد با موفقیت ذخیره شد"})

    return JsonResponse({"success": False, "message": "درخواست نامعتبر است"}, status=400)

#............................Monitoring......................................
def monitoring_center(request):
    latest_teachers = User.objects.filter(role="TEACHER").order_by("-date_joined")[:5]
    latest_logs = ActivityLog.objects.order_by("-created_at")[:10]

    context = {
        "latest_teachers": latest_teachers,
        "admin_last_login": request.user.last_login,
        "latest_logs": latest_logs,
    }

    return render(request, "accounts/monitoring_center.html", context)