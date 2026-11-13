from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ClassRoom
from core.permissions import is_admin, is_teacher
from exams.models import PlacementAnswer, PlacementAttempt, PlacementQuestion, PlacementTest
from students.models import StudentProfile


SUBJECT_LABELS = dict(PlacementQuestion.Subject.choices)


def _teacher_scope(user):
    manager = is_admin(user) or user.is_superuser
    students = StudentProfile.objects.select_related("user", "classroom")
    tests = PlacementTest.objects.all()
    if not manager:
        classrooms = ClassRoom.objects.filter(teacher=user, is_active=True)
        grades = list(classrooms.values_list("grade", flat=True).distinct())
        students = students.filter(
            Q(classroom__in=classrooms) |
            Q(classroom__isnull=True, grade__in=(grades or [6]))
        )
        tests = tests.filter(grade__in=(grades or [6]))
    return students, tests


@login_required(login_url="login")
def teacher_learning_reports(request):
    if not (is_teacher(request.user) or is_admin(request.user) or request.user.is_superuser):
        return redirect("simple-student")

    students, tests = _teacher_scope(request.user)
    student_id = request.GET.get("student", "").strip()
    test_id = request.GET.get("test", "").strip()

    selected_student = None
    selected_test = None
    if student_id:
        selected_student = get_object_or_404(students, pk=student_id)
    if test_id:
        selected_test = get_object_or_404(tests, pk=test_id)

    attempts = PlacementAttempt.objects.filter(
        student__in=students, test__in=tests
    ).select_related("student__user", "student__classroom", "test").order_by(
        "-completed_at", "-id"
    )
    if selected_student:
        attempts = attempts.filter(student=selected_student)
    if selected_test:
        attempts = attempts.filter(test=selected_test)

    attempt_rows = list(attempts[:150])
    attempt_ids = [item.pk for item in attempt_rows]
    answers = PlacementAnswer.objects.filter(
        attempt_id__in=attempt_ids
    ).select_related("attempt__student__user", "attempt__test").order_by("attempt_id", "id")

    subject_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    category_stats = defaultdict(lambda: {"correct": 0, "total": 0, "subject": ""})
    student_stats = {}
    total_correct = 0
    total_answers = 0

    for answer in answers:
        subject = answer.subject or "unknown"
        subject_stats[subject]["total"] += 1
        subject_stats[subject]["correct"] += int(answer.is_correct)
        total_answers += 1
        total_correct += int(answer.is_correct)

        key = (answer.attempt.student_id, answer.attempt.test_id)
        row = student_stats.setdefault(key, {
            "student": answer.attempt.student,
            "test": answer.attempt.test,
            "correct": 0,
            "total": 0,
        })
        row["total"] += 1
        row["correct"] += int(answer.is_correct)

        names = answer.category_names if isinstance(answer.category_names, list) else []
        for depth, name in enumerate(names):
            if not name:
                continue
            category_key = (subject, depth, str(name))
            category_stats[category_key]["subject"] = subject
            category_stats[category_key]["total"] += 1
            category_stats[category_key]["correct"] += int(answer.is_correct)

    subject_rows = []
    for code, stats in subject_stats.items():
        subject_rows.append({
            "name": SUBJECT_LABELS.get(code, code),
            "total": stats["total"],
            "correct": stats["correct"],
            "percentage": round(stats["correct"] * 100 / stats["total"]) if stats["total"] else 0,
        })
    subject_rows.sort(key=lambda row: (row["percentage"], row["name"]))

    level_names = {0: "فصل", 1: "مبحث", 2: "زیرمبحث"}
    category_rows = []
    for (subject, depth, name), stats in category_stats.items():
        total = stats["total"]
        category_rows.append({
            "subject": SUBJECT_LABELS.get(subject, subject),
            "level": level_names.get(depth, f"سطح {depth + 1}"),
            "name": name,
            "total": total,
            "correct": stats["correct"],
            "percentage": round(stats["correct"] * 100 / total) if total else 0,
        })
    category_rows.sort(key=lambda row: (row["percentage"], row["total"], row["name"]))

    performance_rows = []
    for attempt in attempt_rows:
        stats = student_stats.get((attempt.student_id, attempt.test_id))
        if stats and stats["total"]:
            correct, total = stats["correct"], stats["total"]
        else:
            correct, total = attempt.correct_answers, attempt.total_questions
        performance_rows.append({
            "attempt": attempt,
            "correct": correct,
            "total": total,
            "percentage": round(correct * 100 / total) if total else attempt.score,
        })

    return render(request, "simple/teacher_reports.html", {
        "students": students.order_by("user__first_name", "user__last_name"),
        "tests": tests.order_by("-id"),
        "selected_student": selected_student,
        "selected_test": selected_test,
        "subject_rows": subject_rows,
        "category_rows": category_rows[:60],
        "performance_rows": performance_rows,
        "attempt_count": len(attempt_rows),
        "answer_count": total_answers,
        "student_count": len({item.student_id for item in attempt_rows}),
        "overall_percentage": round(total_correct * 100 / total_answers) if total_answers else 0,
    })
