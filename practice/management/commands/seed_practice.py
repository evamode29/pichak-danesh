from django.core.management.base import BaseCommand

from practice.models import PracticeQuestion


QUESTIONS = [
    # ریاضی — سطح ۱
    {
        "subject": "math", "text": "کدام کسر با ۱/۲ برابر است؟", "option_a": "۲/۴", "option_b": "۳/۴", "option_c": "۱/۳", "option_d": "۲/۳", "correct_option": "A", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "math", "text": "حاصل ۲۵ + ۳۷ کدام است؟", "option_a": "۵۲", "option_b": "۶۲", "option_c": "۶۴", "option_d": "۷۲", "correct_option": "B", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "math", "text": "عدد ۰٫۷۵ به صورت کسر کدام است؟", "option_a": "۳/۴", "option_b": "۱/۴", "option_c": "۷/۵", "option_d": "۷۵/۱۰", "correct_option": "A", "level": 1, "difficulty": 2, "points": 10,
    },
    {
        "subject": "math", "text": "محیط مربعی با ضلع ۵ سانتی‌متر چند سانتی‌متر است؟", "option_a": "۱۰", "option_b": "۱۵", "option_c": "۲۰", "option_d": "۲۵", "correct_option": "C", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "math", "text": "کدام عدد بر ۳ بخش‌پذیر است؟", "option_a": "۱۲۴", "option_b": "۱۳۵", "option_c": "۱۴۲", "option_d": "۱۵۱", "correct_option": "B", "level": 1, "difficulty": 2, "points": 10,
    },
    {
        "subject": "math", "text": "حاصل ۶ × ۸ کدام است؟", "option_a": "۴۲", "option_b": "۴۸", "option_c": "۵۴", "option_d": "۵۶", "correct_option": "B", "level": 1, "difficulty": 1, "points": 10,
    },
    # علوم — سطح ۱
    {
        "subject": "science", "text": "کدام مورد یک تغییر فیزیکی است؟", "option_a": "سوختن چوب", "option_b": "زنگ زدن آهن", "option_c": "ذوب شدن یخ", "option_d": "پختن غذا", "correct_option": "C", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "science", "text": "کدام اندام وظیفه پمپاژ خون را بر عهده دارد؟", "option_a": "ریه", "option_b": "قلب", "option_c": "کبد", "option_d": "معده", "correct_option": "B", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "science", "text": "گیاهان برای ساخت غذای خود بیشتر به کدام عامل نیاز دارند؟", "option_a": "نور خورشید", "option_b": "صدا", "option_c": "نمک", "option_d": "شن", "correct_option": "A", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "science", "text": "کدام ماده رسانای خوب برق است؟", "option_a": "چوب", "option_b": "پلاستیک", "option_c": "مس", "option_d": "شیشه", "correct_option": "C", "level": 1, "difficulty": 2, "points": 10,
    },
    {
        "subject": "science", "text": "آب در فشار معمولی در چه دمایی می‌جوشد؟", "option_a": "۰ درجه", "option_b": "۵۰ درجه", "option_c": "۱۰۰ درجه", "option_d": "۲۰۰ درجه", "correct_option": "C", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "science", "text": "کدام نیرو باعث می‌شود اجسام به سمت زمین کشیده شوند؟", "option_a": "اصطکاک", "option_b": "گرانش", "option_c": "مغناطیس", "option_d": "شناوری", "correct_option": "B", "level": 1, "difficulty": 1, "points": 10,
    },
    # فارسی — سطح ۱
    {
        "subject": "persian", "text": "کدام واژه از نظر معنی با «دلیر» نزدیک‌تر است؟", "option_a": "شجاع", "option_b": "خسته", "option_c": "آرام", "option_d": "خاموش", "correct_option": "A", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "persian", "text": "در جمله «دانش‌آموز کتاب را خواند»، نهاد کدام است؟", "option_a": "کتاب", "option_b": "را", "option_c": "خواند", "option_d": "دانش‌آموز", "correct_option": "D", "level": 1, "difficulty": 2, "points": 10,
    },
    {
        "subject": "persian", "text": "کدام واژه جمع است؟", "option_a": "کتاب", "option_b": "دانش‌آموزان", "option_c": "مدرسه", "option_d": "معلم", "correct_option": "B", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "persian", "text": "کدام گزینه یک جمله کامل است؟", "option_a": "در حیاط", "option_b": "کتاب خوب", "option_c": "پرنده پرواز کرد.", "option_d": "صبح زیبا", "correct_option": "C", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "persian", "text": "مخالف واژه «آغاز» کدام است؟", "option_a": "شروع", "option_b": "پایان", "option_c": "ابتدا", "option_d": "نخست", "correct_option": "B", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "persian", "text": "کدام واژه از نظر املایی درست نوشته شده است؟", "option_a": "مسئول", "option_b": "مسول", "option_c": "مسئولل", "option_d": "مسءول", "correct_option": "A", "level": 1, "difficulty": 2, "points": 10,
    },
    # مطالعات اجتماعی — سطح ۱
    {
        "subject": "social", "text": "پایتخت ایران کدام شهر است؟", "option_a": "مشهد", "option_b": "اصفهان", "option_c": "تهران", "option_d": "شیراز", "correct_option": "C", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "social", "text": "کدام مورد یکی از قاره‌های جهان است؟", "option_a": "خلیج فارس", "option_b": "آسیا", "option_c": "دریای خزر", "option_d": "رود نیل", "correct_option": "B", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "social", "text": "کدام مورد برای نشان دادن مکان‌ها و جهت‌ها روی زمین استفاده می‌شود؟", "option_a": "نقشه", "option_b": "تراز", "option_c": "دماسنج", "option_d": "قطب‌نما فقط", "correct_option": "A", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "social", "text": "کدام گزینه یکی از جهت‌های اصلی است؟", "option_a": "بالا", "option_b": "پایین", "option_c": "شمال", "option_d": "داخل", "correct_option": "C", "level": 1, "difficulty": 1, "points": 10,
    },
    {
        "subject": "social", "text": "شهروند خوب در برابر قوانین جامعه چه رفتاری دارد؟", "option_a": "آن‌ها را رعایت می‌کند", "option_b": "آن‌ها را نادیده می‌گیرد", "option_c": "فقط هنگام امتحان رعایت می‌کند", "option_d": "قوانین را تغییر می‌دهد", "correct_option": "A", "level": 1, "difficulty": 2, "points": 10,
    },
    {
        "subject": "social", "text": "کدام مورد نمونه‌ای از منابع طبیعی است؟", "option_a": "آهنگ", "option_b": "آب", "option_c": "کتاب", "option_d": "میز", "correct_option": "B", "level": 1, "difficulty": 1, "points": 10,
    },
    # سطح ۲ — سؤال‌های ترکیبی‌تر
    {
        "subject": "math", "text": "حاصل ۳/۴ + ۱/۴ کدام است؟", "option_a": "۱/۲", "option_b": "۱", "option_c": "۵/۸", "option_d": "۳/۸", "correct_option": "B", "level": 2, "difficulty": 2, "points": 15,
    },
    {
        "subject": "math", "text": "اگر قیمت یک دفتر ۳۰ هزار تومان باشد، قیمت ۳ دفتر چقدر است؟", "option_a": "۶۰ هزار", "option_b": "۷۰ هزار", "option_c": "۹۰ هزار", "option_d": "۱۰۰ هزار", "correct_option": "C", "level": 2, "difficulty": 2, "points": 15,
    },
    {
        "subject": "science", "text": "کدام بخش گیاه بیشتر آب و مواد معدنی را از خاک جذب می‌کند؟", "option_a": "ریشه", "option_b": "گل", "option_c": "میوه", "option_d": "دانه", "correct_option": "A", "level": 2, "difficulty": 2, "points": 15,
    },
    {
        "subject": "science", "text": "در یک مدار ساده، برای روشن شدن لامپ چه چیزی باید کامل باشد؟", "option_a": "مسیر مدار", "option_b": "رنگ سیم", "option_c": "شکل لامپ", "option_d": "اندازه باتری فقط", "correct_option": "A", "level": 2, "difficulty": 2, "points": 15,
    },
    {
        "subject": "persian", "text": "در جمله «پرنده کوچک با سرعت پرواز کرد»، کدام واژه صفت است؟", "option_a": "پرنده", "option_b": "کوچک", "option_c": "سرعت", "option_d": "پرواز", "correct_option": "B", "level": 2, "difficulty": 2, "points": 15,
    },
    {
        "subject": "persian", "text": "کدام گزینه هم‌خانواده «علم» است؟", "option_a": "عالم", "option_b": "قلم", "option_c": "سلام", "option_d": "قلمرو", "correct_option": "A", "level": 2, "difficulty": 2, "points": 15,
    },
    {
        "subject": "social", "text": "مهم‌ترین فایده همکاری اعضای یک جامعه چیست؟", "option_a": "افزایش اختلاف", "option_b": "رسیدن بهتر به هدف‌های مشترک", "option_c": "کاهش مسئولیت‌پذیری", "option_d": "حذف قانون", "correct_option": "B", "level": 2, "difficulty": 2, "points": 15,
    },
    {
        "subject": "social", "text": "کدام مورد می‌تواند به شناخت گذشته یک سرزمین کمک کند؟", "option_a": "آثار تاریخی", "option_b": "چراغ راهنمایی", "option_c": "لوازم ورزشی", "option_d": "بسته‌بندی خوراکی", "correct_option": "A", "level": 2, "difficulty": 2, "points": 15,
    },
]


class Command(BaseCommand):
    help = "بارگذاری سؤال‌های پایه ششم برای تمرین پیچک دانش"

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for item in QUESTIONS:
            defaults = item.copy()
            subject = defaults.pop("subject")
            text = defaults["text"]
            question, was_created = PracticeQuestion.objects.update_or_create(
                subject=subject,
                text=text,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed تمرین کامل شد: {created} سؤال جدید، {updated} سؤال به‌روزرسانی شد."
            )
        )
