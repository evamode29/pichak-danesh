from secrets import choice
from string import ascii_letters, digits

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ClassRoom, UserProfile
from core.permissions import is_teacher
from students.models import StudentProfile


User = get_user_model()

CLASS_STUDENTS = [
    ("ایمان", "ابراهیمی عمارت", "iman01"),
    ("محمدپارسا", "اکبری فرخانی", "mparsa02"),
    ("سجاد", "الیاسی یوسف‌آباد", "sajad03"),
    ("امیرمحمد", "ایزی", "amir04"),
    ("کارن", "بابایی", "karen05"),
    ("مهیار", "بابایی فیروزآباد", "mahyar06"),
    ("امیرعلی", "بیگ‌زاده", "amirali07"),
    ("محمدمهدی", "جعفری تیکانلو", "mmahdi08"),
    ("امیرعباس", "چوپانی", "amirabbas09"),
    ("سجاد", "حسن‌زاده خواجه‌ها", "sajad10"),
    ("محمدرضا", "خان‌زاده", "mreza11"),
    ("سینا", "دام‌آفرین", "sina12"),
    ("سینا یار", "رفیعی کهنه‌رود", "sinayar13"),
    ("امیرمحمد", "رهنمازوباران", "amirm14"),
    ("علی", "زارعی", "ali15"),
    ("افشین", "سهرابی‌فر", "afshin16"),
    ("محمدامین", "شاکری", "mamin17"),
    ("متین", "شریفی", "matin18"),
    ("آرش", "صاحب‌الزمانی", "arsh19"),
    ("محمد", "صبوری‌پور", "mohammad20"),
    ("پرهام", "صفی‌پور", "parham21"),
    ("سیدامیرمحمد", "قربانی موسوی", "samir22"),
    ("امیرعباس", "گودرزی", "amirabbas23"),
    ("محمدمهدی", "محمدی‌زاده", "mmahdi24"),
    ("طاها", "نامی", "taha25"),
    ("محمدصالحا", "نظری", "msaleha26"),
    ("فرمان", "نوحه‌خوان قوچان عتیق", "farman27"),
]


def _temporary_password(length=10):
    alphabet = ascii_letters + digits
    return "Pk-" + "".join(choice(alphabet) for _ in range(length - 3))


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
    credentials = []

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

        elif action == "seed_class":
            classroom_id = request.POST.get("classroom")
            classroom = get_object_or_404(
                ClassRoom, pk=classroom_id, teacher=request.user, is_active=True
            )
            selected_classroom = classroom

            for first_name, last_name, username in CLASS_STUDENTS:
                user = User.objects.filter(username=username).first()
                password = _temporary_password()
                if user is None:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )
                else:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.set_password(password)
                    user.save(update_fields=["first_name", "last_name", "password"])

                UserProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        "role": UserProfile.Role.STUDENT,
                        "mobile": None,
                        "display_name": f"{first_name} {last_name}".strip(),
                    },
                )
                StudentProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        "classroom": classroom,
                        "mobile": None,
                        "grade": classroom.grade,
                        "is_free": True,
                    },
                )
                credentials.append({
                    "name": f"{first_name} {last_name}".strip(),
                    "username": username,
                    "password": password,
                })

            message = f"{len(CLASS_STUDENTS)} حساب دانش‌آموزی برای «{classroom.name}» آماده شد."

        elif action == "add_student":
            classroom_id = request.POST.get("classroom")
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            username = request.POST.get("username", "").strip()
            mobile = request.POST.get("mobile", "").strip() or None
            password = request.POST.get("password", "")
            classroom = get_object_or_404(
                ClassRoom, pk=classroom_id, teacher=request.user, is_active=True
            )
            selected_classroom = classroom

            if not all([first_name, last_name, username, password]):
                error = "نام، نام خانوادگی، نام کاربری و رمز عبور را کامل وارد کنید."
            elif len(password) < 6:
                error = "رمز عبور باید حداقل ۶ کاراکتر باشد."
            elif User.objects.filter(username=username).exists():
                error = "این نام کاربری قبلاً استفاده شده است."
            elif mobile and StudentProfile.objects.filter(mobile=mobile).exists():
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
            "credentials": credentials,
            "student_count": len(CLASS_STUDENTS),
        },
    )
