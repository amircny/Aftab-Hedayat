import pandas as pd

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import EventForm, ExcelUploadForm
from .models import Event, AllowedStudent
from django.http import JsonResponse


# =========================
# داشبورد استاد
# =========================
@login_required
def teacher_dashboard(request):
    events = Event.objects.filter(
        teacher=request.user
    ).order_by("-created_at")

    form = EventForm()

    return render(request, "accounts/dashboard.html", {
        "events": events,
        "form": form
    })


# =========================
# ساخت ایونت
# =========================
@login_required
def create_event(request):

    if request.method == "POST":
        form = EventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.teacher = request.user
            event.save()

            messages.success(request, "ایونت با موفقیت ثبت شد.")
            return redirect("teacher_dashboard")

    return redirect("teacher_dashboard")


# =========================
# آپلود اکسل دانشجو
# =========================
@login_required
def upload_student_excel(request, event_id):
    event = get_object_or_404(Event, id=event_id, teacher=request.user)
    session_key = f"preview_student_ids_{event.id}"

    if request.method == "POST":

        # مرحله تایید نهایی
        if request.POST.get("confirm_upload") == "1":
            preview_student_ids = request.session.get(session_key)

            if not preview_student_ids:
                return render(request, "events/upload_excel.html", {
                    "form": ExcelUploadForm(),
                    "event": event,
                    "error": "ابتدا فایل را آپلود و بررسی کنید."
                })

            AllowedStudent.objects.filter(event=event).delete()

            count = 0
            for sid in preview_student_ids:
                AllowedStudent.objects.create(
                    event=event,
                    student_id=sid
                )
                count += 1

            if session_key in request.session:
                del request.session[session_key]

            messages.success(
                request,
                f"{count} دانشجو ثبت شدند. فقط این شماره‌ها در این جلسه مجاز خواهند بود."
            )
            return redirect("teacher_dashboard")

        # مرحله آپلود + بررسی + پیش نمایش
        form = ExcelUploadForm(request.POST, request.FILES)

        if form.is_valid():
            excel_file = form.cleaned_data["excel_file"]

            if not excel_file:
                return render(request, "events/upload_excel.html", {
                    "form": form,
                    "event": event,
                    "error": "لطفاً یک فایل انتخاب کنید."
                })

            if not excel_file.name.lower().endswith((".xlsx", ".xls")):
                return render(request, "events/upload_excel.html", {
                    "form": form,
                    "event": event,
                    "error": "فرمت فایل باید Excel باشد (.xlsx یا .xls)."
                })

            if excel_file.size == 0:
                return render(request, "events/upload_excel.html", {
                    "form": form,
                    "event": event,
                    "error": "فایل خالی است."
                })

            try:
                df = pd.read_excel(excel_file)
            except Exception:
                return render(request, "events/upload_excel.html", {
                    "form": form,
                    "event": event,
                    "error": "فایل اکسل معتبر نیست یا قابل خواندن نیست."
                })

            if df.empty:
                return render(request, "events/upload_excel.html", {
                    "form": form,
                    "event": event,
                    "error": "محتوای فایل اکسل خالی است."
                })

            if len(df.columns) != 1:
                return render(request, "events/upload_excel.html", {
                    "form": form,
                    "event": event,
                    "error": "فایل اکسل باید دقیقاً فقط یک ستون داشته باشد."
                })

            column_name = str(df.columns[0]).strip()
            if column_name != "student_id":
                return render(request, "events/upload_excel.html", {
                    "form": form,
                    "event": event,
                    "error": "نام ستون باید دقیقاً student_id باشد."
                })

            preview_student_ids = (
                df["student_id"]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )

            preview_student_ids = [sid for sid in preview_student_ids if sid]

            if not preview_student_ids:
                return render(request, "events/upload_excel.html", {
                    "form": form,
                    "event": event,
                    "error": "هیچ student_id معتبری در فایل پیدا نشد."
                })

            request.session[session_key] = preview_student_ids

            return render(request, "events/upload_excel.html", {
                "form": ExcelUploadForm(),
                "event": event,
                "preview_data": preview_student_ids,
                "preview_ready": True
            })

    else:
        form = ExcelUploadForm()

    return render(request, "events/upload_excel.html", {
        "form": form,
        "event": event
    })

# =========================
# حذف ایونت
# =========================
@login_required
def delete_event(request, event_id):

    event = get_object_or_404(Event, id=event_id, teacher=request.user)

    if request.method == "POST":
        event.delete()
        return JsonResponse({
            "success": True,
            "message": "ایونت با موفقیت حذف شد."
        })

    return JsonResponse({
        "success": False,
        "message": "درخواست نامعتبر است."
    }, status=400)

#========================================
@login_required
def event_report(request, event_id):
    return JsonResponse({
        "success": False,
        "message": "فعلاً گزارشی موجود نیست."
    })