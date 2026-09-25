from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.models import DailyTask, StudentTask
from students.models import StudentProfile


@login_required(login_url="login")
def student_homework(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")

    message = None
    error = None

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "mark_done":
            task = get_object_or_404(
                DailyTask,
                pk=request.POST.get("task_id"),
                classroom=student.classroom,
                task_date=date.today(),
            )
            record, _ = StudentTask.objects.get_or_create(task=task, student=student)
            if record.status == StudentTask.Status.PENDING:
                record.status = StudentTask.Status.DONE
                record.save(update_fields=["status", "updated_at"])
                message = f"تکلیف «{task.title}» به‌عنوان انجام‌شده ثبت شد."
            else:
                message = "وضعیت این تکلیف قبلاً ثبت شده است."

    tasks = DailyTask.objects.filter(classroom=student.classroom, task_date=date.today()).prefetch_related("student_tasks") if student.classroom else []
    rows = []
    for task in tasks:
        record, _ = StudentTask.objects.get_or_create(task=task, student=student)
        rows.append({"task": task, "record": record})

    return render(request, "student/homework.html", {
        "student": student,
        "rows": rows,
        "message": message,
        "error": error,
    })
