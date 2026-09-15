from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.models import DailyTask, StudentTask
from students.models import StudentProfile


@login_required(login_url="login")
def student_homework(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")

    tasks = DailyTask.objects.filter(classroom=student.classroom, task_date=date.today()).prefetch_related("student_tasks") if student.classroom else []
    rows = []
    for task in tasks:
        record, _ = StudentTask.objects.get_or_create(task=task, student=student)
        rows.append({"task": task, "record": record})

    return render(request, "student/homework.html", {"student": student, "rows": rows})
