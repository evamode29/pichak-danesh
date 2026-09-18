from collections import defaultdict

from .models import PracticeAttempt


SUBJECT_NAMES = {
    "math": "ریاضی",
    "science": "علوم",
    "persian": "فارسی",
    "social": "مطالعات اجتماعی",
}


def practice_subject_scores(student):
    """Return recent subject performance as {code: {total, correct, accuracy}}."""
    attempts = (
        PracticeAttempt.objects.filter(student=student)
        .select_related("question")
        .order_by("-created_at", "-id")[:40]
    )
    grouped = defaultdict(lambda: {"total": 0, "correct": 0})
    for attempt in attempts:
        subject = attempt.question.subject
        grouped[subject]["total"] += 1
        grouped[subject]["correct"] += int(attempt.is_correct)

    scores = {}
    for subject, data in grouped.items():
        total = data["total"]
        scores[subject] = {
            "total": total,
            "correct": data["correct"],
            "accuracy": round(data["correct"] * 100 / total) if total else 0,
        }
    return scores


def recommended_subject(student, placement_subject=None):
    """Choose the current practice focus, preferring real practice evidence."""
    scores = practice_subject_scores(student)

    eligible = [
        (data["accuracy"], -data["total"], code)
        for code, data in scores.items()
        if data["total"] >= 2
    ]
    if eligible:
        accuracy, _, subject = min(eligible)
        if accuracy < 80:
            return subject

    return placement_subject


def subject_label(subject):
    return SUBJECT_NAMES.get(subject, "تمرین عمومی")
