from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from exams.models import PlacementAttempt
from .adaptive import SUBJECT_NAMES, recommended_subject
from .missions import claim_completed_missions
from .models import PracticeAttempt, PracticeQuestion


def _placement_weak_subject(student):
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


def _practice_questions(student, focus_subject, limit=5):
    """Pick unseen questions first, then allow spaced review when needed."""
    level_min = max(1, student.level - 1)
    level_max = student.level + 1
    available = PracticeQuestion.objects.filter(
        is_active=True,
        level__gte=level_min,
        level__lte=level_max,
    )
    answered_ids = set(
        PracticeAttempt.objects.filter(student=student).values_list("question_id", flat=True)
    )

    def pick(queryset, selected):
        rows = list(queryset.exclude(id__in=selected).order_by("difficulty", "id"))
        unseen = [question for question in rows if question.id not in answered_ids]
        seen = [question for question in rows if question.id in answered_ids]
        return unseen + seen

    selected = []
    if focus_subject:
        selected.extend(pick(available.filter(subject=focus_subject), set())[:limit])

    if len(selected) < limit:
        selected_ids = {question.id for question in selected}
        selected.extend(
            pick(available.exclude(id__in=selected_ids), selected_ids)[: limit - len(selected)]
        )

    if len(selected) < limit:
        selected_ids = {question.id for question in selected}
        fallback = PracticeQuestion.objects.filter(is_active=True)
        if focus_subject:
            fallback = fallback.filter(subject=focus_subject)
        selected.extend(
            pick(fallback, selected_ids)[: limit - len(selected)]
        )

    return selected


@login_required(login_url="login")
def practice_start(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")

    placement_subject = _placement_weak_subject(student)
    focus_subject = recommended_subject(student, placement_subject)
    questions = _practice_questions(student, focus_subject)

    if not questions:
        return render(request, "practice/not_ready.html", {"student": student})

    request.session["practice_question_ids"] = [q.id for q in questions]
    request.session["practice_index"] = 0
    request.session["practice_answers"] = {}
    request.session["practice_weak_subject"] = focus_subject
    request.session["practice_focus_source"] = (
        "practice" if focus_subject and focus_subject != placement_subject else "diagnostic"
    )
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
            "question_options": [
                ("A", question.option_a),
                ("B", question.option_b),
                ("C", question.option_c),
                ("D", question.option_d),
            ],
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
    request.session.pop("practice_focus_source", None)

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
