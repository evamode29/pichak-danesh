from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from students.models import StudentProfile

from .models import DailyMissionCompletion, PracticeAttempt


@dataclass(frozen=True)
class DailyMission:
    code: str
    title: str
    description: str
    target: int
    reward_xp: int
    icon: str


MISSIONS = (
    DailyMission("answer_5", "۵ سؤال حل کن", "امروز به ۵ سؤال تمرینی پاسخ بده.", 5, 20, "📝"),
    DailyMission("correct_3", "۳ پاسخ درست", "حداقل ۳ پاسخ درست ثبت کن.", 3, 30, "🎯"),
    DailyMission("earn_50_xp", "۵۰ XP کسب کن", "امروز حداقل ۵۰ XP به دست بیاور.", 50, 40, "⚡"),
)


def daily_mission_progress(student, mission, *, today=None):
    """Return today's progress for one mission without mutating the student."""
    today = today or timezone.localdate()
    attempts = PracticeAttempt.objects.filter(student=student, created_at__date=today)

    if mission.code == "answer_5":
        value = attempts.count()
    elif mission.code == "correct_3":
        value = attempts.filter(is_correct=True).count()
    elif mission.code == "earn_50_xp":
        value = sum(attempt.points_earned for attempt in attempts)
    else:
        value = 0

    value = min(value, mission.target)
    return {
        "code": mission.code,
        "title": mission.title,
        "description": mission.description,
        "icon": mission.icon,
        "target": mission.target,
        "reward_xp": mission.reward_xp,
        "current": value,
        "percent": min(100, round((value / mission.target) * 100)) if mission.target else 100,
        "completed": value >= mission.target,
    }


def daily_missions(student, *, today=None):
    """Return today's missions including whether their reward was already claimed."""
    today = today or timezone.localdate()
    claimed_codes = set(
        DailyMissionCompletion.objects.filter(
            student=student,
            mission_date=today,
        ).values_list("mission_code", flat=True)
    )

    missions = []
    for mission in MISSIONS:
        progress = daily_mission_progress(student, mission, today=today)
        progress["claimed"] = mission.code in claimed_codes
        missions.append(progress)
    return missions


@transaction.atomic
def claim_completed_missions(student, *, today=None):
    """Claim newly completed daily missions and award their XP exactly once."""
    today = today or timezone.localdate()
    locked_student = StudentProfile.objects.select_for_update().get(pk=student.pk)
    claimed = []

    for mission in MISSIONS:
        progress = daily_mission_progress(locked_student, mission, today=today)
        if not progress["completed"]:
            continue

        completion, created = DailyMissionCompletion.objects.get_or_create(
            student=locked_student,
            mission_code=mission.code,
            mission_date=today,
            defaults={"reward_xp": mission.reward_xp},
        )
        if created:
            claimed.append(mission)

    reward_xp = sum(mission.reward_xp for mission in claimed)
    if reward_xp:
        locked_student.xp += reward_xp
        locked_student.refresh_level()
        locked_student.save(update_fields=["xp", "level", "updated_at"])

    return claimed
