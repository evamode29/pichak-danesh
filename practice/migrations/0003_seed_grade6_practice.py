from django.db import migrations


QUESTIONS = [
    ("math", "حاصل ۳۵ + ۲۷ کدام است؟", "۵۲", "۶۲", "۶۳", "۷۲", "B", 1, 1, 10),
    ("math", "نصف ۸۰ چند است؟", "۲۰", "۳۰", "۴۰", "۵۰", "C", 1, 1, 10),
    ("math", "محیط مربع با ضلع ۶ سانتی‌متر چند است؟", "۱۲", "۱۸", "۲۴", "۳۶", "C", 1, 1, 10),
    ("math", "حاصل ۴۸ ÷ ۶ × ۲ کدام است؟", "۴", "۸", "۱۲", "۱۶", "D", 2, 2, 12),
    ("math", "اگر قیمت هر دفتر ۲۵ هزار تومان باشد، ۳ دفتر چقدر می‌شود؟", "۵۰ هزار", "۷۵ هزار", "۸۰ هزار", "۱۰۰ هزار", "B", 2, 1, 10),
    ("science", "کدام مورد برای رشد گیاه ضروری است؟", "نور خورشید", "صدا", "نمک", "پلاستیک", "A", 1, 1, 10),
    ("science", "کدام اندام خون را در بدن پمپاژ می‌کند؟", "ریه", "معده", "قلب", "کبد", "C", 1, 1, 10),
    ("science", "آب در دمای معمولی چه حالتی دارد؟", "جامد", "مایع", "گاز", "پلاسما", "B", 1, 1, 10),
    ("science", "نیرویی که اجسام را به سوی زمین می‌کشد چیست؟", "اصطکاک", "گرانش", "مغناطیس", "فشار", "B", 2, 1, 10),
    ("science", "کدام زنجیره غذایی درست است؟", "قورباغه ← علف ← ملخ", "علف ← ملخ ← قورباغه", "ملخ ← علف ← قورباغه", "علف ← قورباغه ← ملخ", "B", 2, 2, 12),
    ("persian", "هم‌معنی «آغاز» کدام است؟", "پایان", "شروع", "میانه", "توقف", "B", 1, 1, 10),
    ("persian", "در جمله «دانش‌آموز کتاب را خواند» نهاد کدام است؟", "کتاب", "را", "دانش‌آموز", "خواند", "C", 1, 1, 10),
    ("persian", "کدام جمله کامل و درست است؟", "امروز هوا", "امروز خوب", "هوا امروز", "امروز هوا خوب است.", "D", 1, 1, 10),
    ("persian", "املای درست کدام است؟", "مسول", "مسئول", "مسؤولل", "مسئولّ", "B", 2, 2, 12),
    ("persian", "کدام واژه نام یک رنگ است؟", "آبی", "کتاب", "دویدن", "بلند", "A", 1, 1, 10),
    ("social", "جهت اصلی روبه‌روی جنوب چیست؟", "شرق", "غرب", "شمال", "جنوب", "C", 1, 1, 10),
    ("social", "ایران در کدام قاره قرار دارد؟", "اروپا", "آسیا", "آفریقا", "آمریکا", "B", 1, 1, 10),
    ("social", "کدام مورد یک منبع طبیعی است؟", "رودخانه", "رایانه", "صندلی", "مداد", "A", 1, 1, 10),
    ("social", "کدام رفتار نمونه‌ای از همکاری است؟", "انجام همه کارها توسط یک نفر", "کمک و تقسیم مسئولیت‌ها", "بی‌توجهی به گروه", "جلوگیری از مشارکت دیگران", "B", 2, 1, 10),
    ("social", "میراث فرهنگی به چه چیزی گفته می‌شود؟", "فقط وسایل جدید", "آثار و بناهای ارزشمند به‌جامانده از گذشته", "وسایل مصرفی روزانه", "فقط کتاب‌های درسی", "B", 2, 2, 12),
]


def seed(apps, schema_editor):
    PracticeQuestion = apps.get_model("practice", "PracticeQuestion")
    for subject, text, a, b, c, d, correct, level, difficulty, points in QUESTIONS:
        PracticeQuestion.objects.get_or_create(
            subject=subject,
            text=text,
            defaults={
                "option_a": a,
                "option_b": b,
                "option_c": c,
                "option_d": d,
                "correct_option": correct,
                "level": level,
                "difficulty": difficulty,
                "points": points,
                "is_active": True,
            },
        )


def unseed(apps, schema_editor):
    PracticeQuestion = apps.get_model("practice", "PracticeQuestion")
    texts = [row[1] for row in QUESTIONS]
    PracticeQuestion.objects.filter(text__in=texts).delete()


class Migration(migrations.Migration):
    dependencies = [("practice", "0002_rename_practice_pr_student_3e54a4_idx_practice_pr_student_57b392_idx_and_more")]
    operations = [migrations.RunPython(seed, unseed)]
