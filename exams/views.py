from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.permissions import is_teacher
from .models import PlacementAttempt, PlacementDiagnosticResult, PlacementQuestion, PlacementTest


def _level_from_score(score):
    if score >= 90:
        return 10
    if score >= 80:
        return 8
    if score >= 70:
        return 7
    if score >= 60:
        return 5
    if score >= 50:
        return 4
    if score >= 40:
        return 3
    if score >= 30:
        return 2
    return 1


def _diagnostic_analysis(questions, answers):
    subject_data = defaultdict(lambda: {"correct": 0, "total": 0})
    topic_data = defaultdict(lambda: {"subject": "", "topic": "", "skill": "", "correct": 0, "total": 0})

    for question in questions:
        is_correct = answers.get(str(question.id)) == question.correct_option
        subject = question.subject
        subject_data[subject]["total"] += 1
        subject_data[subject]["correct"] += int(is_correct)
        key = (question.subject, question.topic or "بدون مبحث", question.skill or "")
        topic_data[key]["subject"] = question.get_subject_display()
        topic_data[key]["topic"] = question.topic or "بدون مبحث"
        topic_data[key]["skill"] = question.skill
        topic_data[key]["total"] += 1
        topic_data[key]["correct"] += int(is_correct)

    subject_order = ["math", "science", "persian", "social"]
    subject_names = dict(PlacementQuestion.Subject.choices)
    subjects = []
    for code in subject_order:
        data = subject_data.get(code, {"correct": 0, "total": 0})
        total = data["total"]
        percentage = round(data["correct"] * 100 / total) if total else 0
        subjects.append({"code": code, "name": subject_names.get(code, code), "correct": data["correct"], "total": total, "percentage": percentage})

    topics = []
    for item in topic_data.values():
        percentage = round(item["correct"] * 100 / item["total"]) if item["total"] else 0
        topics.append({**item, "percentage": percentage})
    topics.sort(key=lambda item: (item["percentage"], item["subject"], item["topic"]))
    strengths = [item for item in topics if item["percentage"] >= 80]
    weaknesses = [item for item in topics if item["percentage"] < 60]
    recommendations = [{"subject": item["subject"], "topic": item["topic"], "skill": item["skill"]} for item in weaknesses[:4]]
    return subjects, topics, strengths, weaknesses, recommendations


@login_required(login_url="login")
def placement_start(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")
    test = PlacementTest.objects.filter(grade=student.grade, is_active=True).first()
    if not test:
        return render(request, "placement/not_ready.html")
    if request.method == "POST":
        request.session["placement_test_id"] = test.id
        request.session["placement_answers"] = {}
        return redirect("placement-question")
    return render(request, "placement/start.html", {"test": test, "question_count": test.questions.filter(is_active=True).count()})


@login_required(login_url="login")
def placement_question(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")
    test_id = request.session.get("placement_test_id")
    if not test_id:
        return redirect("placement-start")
    test = get_object_or_404(PlacementTest, id=test_id, grade=student.grade, is_active=True)
    questions = list(test.questions.filter(is_active=True))
    if not questions:
        return render(request, "placement/not_ready.html")
    index = int(request.GET.get("q", 0))
    index = max(0, min(index, len(questions) - 1))
    question = questions[index]
    answers = request.session.get("placement_answers", {})
    if request.method == "POST":
        selected = request.POST.get("answer", "").upper()
        if selected in {"A", "B", "C", "D"}:
            answers[str(question.id)] = selected
            request.session["placement_answers"] = answers
        navigation = request.POST.get("navigation", "next")
        if navigation == "back" and index > 0:
            return redirect(f"/placement/question/?q={index - 1}")
        if navigation == "next" and index + 1 < len(questions):
            return redirect(f"/placement/question/?q={index + 1}")
        return redirect("placement-result")
    return render(request, "placement/question.html", {"test": test, "question": question, "index": index, "total": len(questions), "selected": answers.get(str(question.id))})


@login_required(login_url="login")
def placement_result(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")
    test_id = request.session.get("placement_test_id")
    if not test_id:
        return redirect("placement-start")
    test = get_object_or_404(PlacementTest, id=test_id, grade=student.grade, is_active=True)
    questions = list(test.questions.filter(is_active=True))
    answers = request.session.get("placement_answers", {})
    correct = sum(1 for q in questions if answers.get(str(q.id)) == q.correct_option)
    total = len(questions)
    score = round((correct / total) * 100) if total else 0
    level = _level_from_score(score)
    attempt = PlacementAttempt.objects.create(student=student, test=test, score=score, correct_answers=correct, total_questions=total, level=level)

    subjects, topics, strengths, weaknesses, recommendations = _diagnostic_analysis(questions, answers)
    PlacementDiagnosticResult.objects.bulk_create([
        PlacementDiagnosticResult(
            attempt=attempt,
            subject=question.subject,
            topic=question.topic or "بدون مبحث",
            skill=question.skill,
            correct_answers=sum(1 for q in questions if q.subject == question.subject and (q.topic or "بدون مبحث") == (question.topic or "بدون مبحث") and (q.skill or "") == (question.skill or "") and answers.get(str(q.id)) == q.correct_option),
            total_questions=sum(1 for q in questions if q.subject == question.subject and (q.topic or "بدون مبحث") == (question.topic or "بدون مبحث") and (q.skill or "") == (question.skill or "")),
            percentage=next(item["percentage"] for item in topics if item["subject"] == question.get_subject_display() and item["topic"] == (question.topic or "بدون مبحث") and item["skill"] == question.skill),
        )
        for question in { (q.subject, q.topic or "بدون مبحث", q.skill): q for q in questions }.values()
    ])
    student.level = level
    student.points = max(student.points, score * 10)
    student.save(update_fields=["level", "points", "updated_at"])
    request.session.pop("placement_test_id", None)
    request.session.pop("placement_answers", None)
    return render(request, "placement/result.html", {"attempt": attempt, "student": student, "subjects": subjects, "topics": topics, "strengths": strengths, "weaknesses": weaknesses, "recommendations": recommendations})


@login_required(login_url="login")
def placement_answer_key(request, attempt_id):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("dashboard")
    attempt = get_object_or_404(PlacementAttempt.objects.select_related("test", "approved_by"), pk=attempt_id, student=student)
    if not attempt.answer_key_published:
        return render(request, "placement/answer_key_locked.html", {"attempt": attempt})
    questions = list(attempt.test.questions.filter(is_active=True))
    return render(request, "placement/answer_key.html", {"attempt": attempt, "questions": questions})


@login_required(login_url="login")
def teacher_approve_placement(request, attempt_id):
    if not is_teacher(request.user):
        return redirect("dashboard")
    if request.method != "POST":
        return redirect("teacher-dashboard")
    attempt = get_object_or_404(PlacementAttempt, pk=attempt_id, student__classroom__teacher=request.user)
    attempt.answer_key_published = True
    attempt.approved_by = request.user
    attempt.approved_at = timezone.now()
    attempt.save(update_fields=["answer_key_published", "approved_by", "approved_at"])
    return redirect("teacher-student-detail", student_id=attempt.student_id)
