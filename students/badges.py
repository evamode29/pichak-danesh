from dataclasses import dataclass


@dataclass(frozen=True)
class Badge:
    code: str
    title: str
    description: str
    icon: str


BADGES = (
    Badge("first_step", "اولین قدم", "اولین تمرینت را با موفقیت ثبت کردی.", "🚀"),
    Badge("level_2", "سطح ۲", "به سطح دوم رسیدی.", "⭐"),
    Badge("level_5", "پیشرو", "به سطح پنجم رسیدی.", "🏆"),
    Badge("xp_500", "XP‌خور حرفه‌ای", "حداقل ۵۰۰ XP به دست آوردی.", "⚡"),
)


def earned_badges(student):
    """Return badges earned from the student's current progress."""
    earned = []
    for badge in BADGES:
        if badge.code == "first_step" and student.points < 1:
            continue
        if badge.code == "level_2" and student.level < 2:
            continue
        if badge.code == "level_5" and student.level < 5:
            continue
        if badge.code == "xp_500" and student.xp < 500:
            continue
        earned.append(badge)
    return earned
