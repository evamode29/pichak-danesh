from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import PlacementAttempt


SUBJECT_NAMES = {
    "math": "ریاضی",
    "science": "علوم",
    "persian": "فارسی",
    "social": "مطالعات اجتماعی",
}


def _analysis_context(attempt):
    results = list(attempt.diagnostic_results.all())
    subjects = []
    for code, name in SUBJECT_NAMES.items():
        rows = [row for row in results if row.subject == code]
        total = sum(row.total_questions for row in rows)
        correct = sum(row.correct_answers for row in rows)
        subjects.append({
            "code": code,
            "name": name,
            "correct": correct,
            "total": total,
            "percentage": round(correct * 100 / total) if total else 0,
        })

    topics = []
    for row in results:
        topics.append({
            "subject": SUBJECT_NAMES.get(row.subject, row.subject),
            "topic": row.topic or "بدون مبحث",
            "skill": row.skill,
            "correct": row.correct_answers,
            "total": row.total_questions,
            "percentage": row.percentage,
        })
    topics.sort(key=lambda item: (item["percentage"], item["subject"], item["topic"]))
    weaknesses = [item for item in topics if item["percentage"] < 60]
    strengths = [item for item in topics if item["percentage"] >= 80]
    recommendations = [
        {"subject": item["subject"], "topic": item["topic"], "skill": item["skill"]}
        for item in weaknesses[:4]
    ]

    return {
        "attempt": attempt,
        "student": attempt.student,
        "subjects": subjects,
        "topics": topics,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
    }


@login_required(login_url="login")
def placement_history(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")
    attempts = list(
        PlacementAttempt.objects.filter(student=student)
        .select_related("test")
        .prefetch_related("diagnostic_results")
        .order_by("-completed_at", "-id")
    )
    return render(request, "placement/history.html", {"attempts": attempts})


@login_required(login_url="login")
def placement_result_history(request, attempt_id):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")
    attempt = get_object_or_404(
        PlacementAttempt.objects.select_related("test", "student").prefetch_related("diagnostic_results"),
        pk=attempt_id,
        student=student,
    )
    return render(request, "placement/result.html", _analysis_context(attempt))
