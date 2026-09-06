from dataclasses import dataclass
from datetime import date

from django.db.models import Q

from .models import PracticeAttempt


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
    today = today or date.today()
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
    return [daily_mission_progress(student, mission, today=today) for mission in MISSIONS]
