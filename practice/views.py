from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from exams.models import PlacementAttempt
from .missions import claim_completed_missions
from .models import PracticeAttempt, PracticeQuestion


SUBJECT_NAMES = {
    "math": "ریاضی",
    "science": "علوم",
    "persian": "فارسی",
    "social": "مطالعات اجتماعی",
}


def _weak_subject(student):
    attempt = PlacementAttempt.objects.filter(student=student).prefetch_related("diagnostic_results").first()
    if not attempt:
        return None
    scores = {}
    for row in attempt.diagnostic_results.all():
        scores.setdefault(row.subject, [0, 0])
        scores[row.subject][0] += row.correct_answers
        scores[row.subject][1] += row.total_questions
    valid = [(code, correct * 100 / total) for code, (correct, total) in scores.items() if total]
    return min(valid, key=lambda item: item[1])[0] if valid else None


@login_required(login_url="login")
def practice_start(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")

    weak_subject = _weak_subject(student)
    answered_ids = PracticeAttempt.objects.filter(student=student).values_list("question_id", flat=True)
    base = PracticeQuestion.objects.filter(is_active=True, level__lte=student.level + 1, level__gte=max(1, student.level - 1)).exclude(id__in=answered_ids)

    questions = []
    if weak_subject:
        questions = list(base.filter(subject=weak_subject).order_by("difficulty", "id")[:5])
    if len(questions) < 5:
        extra = list(base.exclude(id__in=[q.id for q in questions]).order_by("difficulty", "subject", "id")[: 5 - len(questions)])
        questions.extend(extra)
    if len(questions) < 5:
        fallback = PracticeQuestion.objects.filter(is_active=True).order_by("difficulty", "subject", "id")
        questions.extend(list(fallback.exclude(id__in=[q.id for q in questions])[: 5 - len(questions)]))

    if not questions:
        return render(request, "practice/not_ready.html", {"student": student})

    request.session["practice_question_ids"] = [q.id for q in questions]
    request.session["practice_index"] = 0
    request.session["practice_answers"] = {}
    request.session["practice_weak_subject"] = weak_subject
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
        timed_out = request.POST.get("timeout") == "1"
        if selected in {"A", "B", "C", "D"}:
            answers[str(question.id)] = selected
            request.session["practice_answers"] = answers
        if timed_out or selected in {"A", "B", "C", "D"}:
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
            "weak_subject": request.session.get("practice_weak_subject"),
            "question_options": [("A", question.option_a), ("B", question.option_b), ("C", question.option_c), ("D", question.option_d)],
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
    answered = 0
    earned = 0
    for question_id in question_ids:
        question = by_id.get(question_id)
        selected = answers.get(str(question_id))
        if not question or selected not in {"A", "B", "C", "D"}:
            continue
        answered += 1
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
    old_level = student.level
    student.points += earned
    student.xp += earned
    student.refresh_level()
    student.save(update_fields=["points", "xp", "level", "updated_at"])
    level_up = student.level > old_level
    mission_rewards = claim_completed_missions(student)
    mission_reward_xp = sum(mission.reward_xp for mission in mission_rewards)

    weak_subject = request.session.get("practice_weak_subject")
    request.session.pop("practice_question_ids", None)
    request.session.pop("practice_index", None)
    request.session.pop("practice_answers", None)
    request.session.pop("practice_weak_subject", None)

    return render(request, "practice/result.html", {
        "student": student,
        "correct": correct,
        "answered": answered,
        "total": total,
        "percent": percent,
        "earned": earned,
        "mission_rewards": mission_rewards,
        "mission_reward_xp": mission_reward_xp,
        "level_up": level_up,
        "old_level": old_level,
        "weak_subject_name": SUBJECT_NAMES.get(weak_subject),
    })
