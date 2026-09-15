from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ClassRoom, UserProfile
from core.permissions import is_teacher
from students.models import StudentProfile


User = get_user_model()


@login_required(login_url="login")
@transaction.atomic
def teacher_class_manage(request):
    if not is_teacher(request.user):
        return redirect("dashboard")

    classrooms = list(
        ClassRoom.objects.filter(teacher=request.user, is_active=True).order_by("grade", "name")
    )
    message = None
    error = None
    selected_classroom = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_class":
            name = request.POST.get("class_name", "").strip()
            academic_year = request.POST.get("academic_year", "1405-1406").strip()
            if not name:
                error = "نام کلاس را وارد کنید."
            else:
                ClassRoom.objects.create(
                    name=name,
                    grade=6,
                    academic_year=academic_year,
                    teacher=request.user,
                    is_active=True,
                )
                message = "کلاس امسال با موفقیت ساخته شد."
                classrooms = list(
                    ClassRoom.objects.filter(teacher=request.user, is_active=True).order_by("grade", "name")
                )

        elif action == "add_student":
            classroom_id = request.POST.get("classroom")
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            username = request.POST.get("username", "").strip()
            mobile = request.POST.get("mobile", "").strip()
            password = request.POST.get("password", "")
            classroom = get_object_or_404(
                ClassRoom, pk=classroom_id, teacher=request.user, is_active=True
            )
            selected_classroom = classroom

            if not all([first_name, last_name, username, mobile, password]):
                error = "نام، نام خانوادگی، نام کاربری، موبایل و رمز عبور را کامل وارد کنید."
            elif len(password) < 6:
                error = "رمز عبور باید حداقل ۶ کاراکتر باشد."
            elif User.objects.filter(username=username).exists():
                error = "این نام کاربری قبلاً استفاده شده است."
            elif StudentProfile.objects.filter(mobile=mobile).exists():
                error = "این شماره موبایل قبلاً برای یک دانش‌آموز ثبت شده است."
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                UserProfile.objects.create(
                    user=user,
                    role=UserProfile.Role.STUDENT,
                    mobile=mobile,
                    display_name=f"{first_name} {last_name}".strip(),
                )
                StudentProfile.objects.create(
                    user=user,
                    classroom=classroom,
                    mobile=mobile,
                    grade=classroom.grade,
                    is_free=True,
                )
                message = f"دانش‌آموز {first_name} {last_name} با موفقیت ثبت شد."

    return render(
        request,
        "teacher/class_manage.html",
        {
            "classrooms": classrooms,
            "selected_classroom": selected_classroom,
            "message": message,
            "error": error,
        },
    )
