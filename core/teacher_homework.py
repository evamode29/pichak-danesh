from datetime import date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ClassRoom, DailyTask, StudentTask
from core.permissions import is_teacher
from students.models import StudentProfile


STUDENTS = [
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


@login_required(login_url="login")
@transaction.atomic
def teacher_homework(request):
    if not is_teacher(request.user):
        return redirect("dashboard")

    classrooms = list(ClassRoom.objects.filter(teacher=request.user, is_active=True).order_by("grade", "name"))
    if not classrooms:
        return redirect("teacher-class-manage")

    classroom_id = request.POST.get("classroom") or request.GET.get("classroom") or classrooms[0].id
    classroom = get_object_or_404(ClassRoom, pk=classroom_id, teacher=request.user, is_active=True)
    selected_date = request.POST.get("task_date") or request.GET.get("date") or date.today().isoformat()
    try:
        task_date = date.fromisoformat(selected_date)
    except ValueError:
        task_date = date.today()
        selected_date = task_date.isoformat()

    message = None
    error = None
    credentials = []

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_task":
            title = request.POST.get("title", "").strip()
            description = request.POST.get("description", "").strip()
            try:
                max_score = max(1, int(request.POST.get("max_score", "20")))
            except ValueError:
                max_score = 20
            if not title:
                error = "عنوان تکلیف را وارد کنید."
            else:
                task = DailyTask.objects.create(
                    classroom=classroom, title=title, description=description,
                    task_date=task_date, max_score=max_score, created_by=request.user,
                )
                for student in StudentProfile.objects.filter(classroom=classroom):
                    StudentTask.objects.create(task=task, student=student)
                message = "تکلیف برای همه دانش‌آموزان کلاس ثبت شد."

        elif action == "save_rows":
            task = get_object_or_404(DailyTask, pk=request.POST.get("task_id"), classroom=classroom)
            students = StudentProfile.objects.filter(classroom=classroom).select_related("user")
            for student in students:
                status = request.POST.get(f"status_{student.id}", StudentTask.Status.PENDING)
                if status not in {choice[0] for choice in StudentTask.Status.choices}:
                    status = StudentTask.Status.PENDING
                raw_score = request.POST.get(f"score_{student.id}", "").strip()
                try:
                    score = int(raw_score) if raw_score else None
                    if score is not None:
                        score = max(0, min(task.max_score, score))
                except ValueError:
                    score = None
                note = request.POST.get(f"note_{student.id}", "").strip()[:500]
                StudentTask.objects.update_or_create(
                    task=task, student=student,
                    defaults={"status": status, "score": score, "note": note},
                )
            message = "وضعیت تکلیف دانش‌آموزان ذخیره شد."

        elif action == "create_students":
            for first_name, last_name, username in STUDENTS:
                if StudentProfile.objects.filter(user__username=username).exists():
                    continue
                if request.user.username == username:
                    continue
                password = f"P{request.user.id or 1}-{username}-x7"
                user = request.user.__class__.objects.create_user(
                    username=username, password=password, first_name=first_name, last_name=last_name,
                )
                from core.models import UserProfile
                UserProfile.objects.create(user=user, role=UserProfile.Role.STUDENT, display_name=f"{first_name} {last_name}")
                StudentProfile.objects.create(user=user, classroom=classroom, grade=classroom.grade, is_free=True)
                credentials.append({"name": f"{first_name} {last_name}", "username": username, "password": password})
            message = f"حساب‌های آماده‌نشده ساخته شدند؛ {len(credentials)} حساب جدید ایجاد شد."

    tasks = list(DailyTask.objects.filter(classroom=classroom, task_date=task_date).order_by("-id"))
    selected_task = tasks[0] if tasks else None
    rows = []
    if selected_task:
        records = {r.student_id: r for r in selected_task.student_tasks.all()}
        for student in StudentProfile.objects.filter(classroom=classroom).select_related("user").order_by("user__first_name", "user__last_name"):
            record = records.get(student.id)
            if not record:
                record = StudentTask.objects.create(task=selected_task, student=student)
            rows.append({"student": student, "record": record})

    return render(request, "teacher/homework.html", {
        "classrooms": classrooms, "classroom": classroom, "task_date": selected_date,
        "tasks": tasks, "selected_task": selected_task, "rows": rows,
        "message": message, "error": error, "credentials": credentials,
        "student_count": StudentProfile.objects.filter(classroom=classroom).count(),
    })
