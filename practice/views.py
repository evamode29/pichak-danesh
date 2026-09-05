from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import PracticeAttempt, PracticeQuestion


@login_required(login_url="login")
def practice_start(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")

    questions = list(
        PracticeQuestion.objects.filter(
            level=student.level,
            is_active=True,
        ).order_by("subject", "id")[:5]
    )
    if len(questions) < 5:
        questions = list(
            PracticeQuestion.objects.filter(
                level__lte=student.level + 1,
                level__gte=max(1, student.level - 1),
                is_active=True,
            ).order_by("level", "subject", "id")[:5]
        )
    if not questions:
        return render(request, "practice/not_ready.html", {"student": student})

    request.session["practice_question_ids"] = [q.id for q in questions]
    request.session["practice_index"] = 0
    request.session["practice_answers"] = {}
    return redirect("practice-question")


@login_required(login_url="login")
def practice_question(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")

    question_ids = request.session.get("practice_question_ids", [])
    if not question_ids:
        return redirect("practice-start")

    index = int(request.GET.get("q", request.session.get("practice_index", 0)))
    index = max(0, min(index, len(question_ids) - 1))
    question = get_object_or_404(PracticeQuestion, id=question_ids[index], is_active=True)
    answers = request.session.get("practice_answers", {})

    if request.method == "POST":
        selected = request.POST.get("answer", "").upper()
        if selected in {"A", "B", "C", "D"}:
            answers[str(question.id)] = selected
            request.session["practice_answers"] = answers
            request.session["practice_index"] = index + 1
            if index + 1 < len(question_ids):
                return redirect(f"/practice/question/?q={index + 1}")
            return redirect("practice-result")

    return render(
        request,
        "practice/question.html",
        {
            "question": question,
            "index": index,
            "total": len(question_ids),
            "selected": answers.get(str(question.id)),
            "student": student,
        },
    )


@login_required(login_url="login")
def practice_result(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")

    question_ids = request.session.get("practice_question_ids", [])
    answers = request.session.get("practice_answers", {})
    if not question_ids:
        return redirect("practice-start")

    questions = list(PracticeQuestion.objects.filter(id__in=question_ids, is_active=True))
    by_id = {q.id: q for q in questions}
    correct = 0
    earned = 0
    for question_id in question_ids:
        question = by_id.get(question_id)
        selected = answers.get(str(question_id))
        if not question or selected not in {"A", "B", "C", "D"}:
            continue
        is_correct = selected == question.correct_option
        if is_correct:
            correct += 1
            earned += question.points
        PracticeAttempt.objects.create(
            student=student,
            question=question,
            selected_option=selected,
            is_correct=is_correct,
            points_earned=question.points if is_correct else 0,
        )

    total = len(question_ids)
    percent = round((correct / total) * 100) if total else 0
    student.points += earned
    student.save(update_fields=["points", "updated_at"])

    request.session.pop("practice_question_ids", None)
    request.session.pop("practice_index", None)
    request.session.pop("practice_answers", None)

    return render(
        request,
        "practice/result.html",
        {
            "student": student,
            "correct": correct,
            "total": total,
            "percent": percent,
            "earned": earned,
        },
    )
