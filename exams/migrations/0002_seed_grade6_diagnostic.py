from django.db import migrations


def seed_grade6_diagnostic(apps, schema_editor):
    PlacementTest = apps.get_model("exams", "PlacementTest")
    PlacementQuestion = apps.get_model("exams", "PlacementQuestion")

    title = "آزمون تشخیصی شروع ششم"
    test, _ = PlacementTest.objects.update_or_create(
        title=title,
        defaults={
            "grade": 6,
            "duration_minutes": 20,
            "is_active": True,
        },
    )

    questions = [
        (1, "math", 1, "کدام کسر با ۱/۲ برابر است؟", "۲/۴", "۳/۴", "۲/۳", "۱/۳", "A"),
        (2, "math", 1, "حاصل ۳۵ + ۲۷ کدام است؟", "۵۲", "۶۲", "۶۴", "۷۲", "B"),
        (3, "math", 2, "محیط مربعی با ضلع ۶ سانتی‌متر چند سانتی‌متر است؟", "۱۲", "۱۸", "۲۴", "۳۶", "C"),
        (4, "math", 2, "اگر ۳ دفتر هرکدام ۲۵ هزار تومان باشد، مجموع قیمت چند تومان است؟", "۵۰ هزار", "۷۵ هزار", "۸۰ هزار", "۱۰۰ هزار", "B"),
        (5, "math", 3, "حاصل ۴۸ ÷ ۶ × ۲ کدام است؟", "۴", "۸", "۱۶", "۲۴", "C"),
        (6, "science", 1, "کدام مورد برای رشد بیشتر گیاه ضروری است؟", "نور خورشید", "صدای بلند", "شن", "نمک", "A"),
        (7, "science", 1, "کدام اندام وظیفه پمپاژ خون در بدن را دارد؟", "ریه", "معده", "قلب", "کبد", "C"),
        (8, "science", 2, "آب در دمای معمولی اتاق بیشتر در کدام حالت است؟", "جامد", "مایع", "گاز", "پلاسما", "B"),
        (9, "science", 2, "کدام نیرو باعث می‌شود اجسام به سمت زمین کشیده شوند؟", "اصطکاک", "مغناطیسی", "گرانش", "کشسانی", "C"),
        (10, "science", 3, "کدام زنجیره یک نمونه ساده از زنجیره غذایی درست است؟", "علف ← ملخ ← قورباغه", "قورباغه ← علف ← ملخ", "ملخ ← علف ← قورباغه", "علف ← قورباغه ← ملخ", "A"),
        (11, "persian", 1, "کدام واژه از نظر معنی به «آغاز» نزدیک‌تر است؟", "پایان", "شروع", "میانه", "توقف", "B"),
        (12, "persian", 1, "در جمله «دانش‌آموز کتاب را خواند»، فاعل کدام است؟", "کتاب", "را", "خواند", "دانش‌آموز", "D"),
        (13, "persian", 2, "کدام گزینه یک جمله کامل و درست است؟", "به مدرسه.", "امروز هوا خوب است.", "اگر فردا.", "کتاب جدید را", "B"),
        (14, "persian", 2, "کدام واژه از نظر املایی درست نوشته شده است؟", "مسئول", "مسول", "مسئولل", "مسعول", "A"),
        (15, "persian", 3, "در عبارت «آسمان آبی و صاف بود»، واژه «آبی» چه چیزی را درباره آسمان بیان می‌کند؟", "زمان", "رنگ", "مکان", "تعداد", "B"),
        (16, "social", 1, "کدام مورد یکی از جهت‌های اصلی جغرافیایی است؟", "بالا", "پایین", "شمال", "کنار", "C"),
        (17, "social", 1, "ایران در کدام قاره قرار دارد؟", "آسیا", "اروپا", "آفریقا", "آمریکا", "A"),
        (18, "social", 2, "کدام مورد یک منبع طبیعی است؟", "رودخانه", "مداد", "دفتر", "صندلی", "A"),
        (19, "social", 2, "برای همکاری بهتر در جامعه، کدام رفتار مناسب‌تر است؟", "رعایت نوبت", "نادیده گرفتن قانون", "قطع کردن صحبت دیگران", "بی‌توجهی به مسئولیت", "A"),
        (20, "social", 3, "کدام گزینه بیشتر به مفهوم «میراث فرهنگی» نزدیک است؟", "یک وسیله کاملاً نو", "آثار و بناهای ارزشمند به‌جامانده از گذشته", "یک برنامه روزانه", "یک وسیله مصرفی یک‌بارمصرف", "B"),
    ]

    PlacementQuestion.objects.filter(test=test).delete()
    PlacementQuestion.objects.bulk_create([
        PlacementQuestion(
            test=test,
            order=order,
            subject=subject,
            difficulty=difficulty,
            text=text,
            option_a=a,
            option_b=b,
            option_c=c,
            option_d=d,
            correct_option=correct,
            is_active=True,
        )
        for order, subject, difficulty, text, a, b, c, d, correct in questions
    ])


def remove_grade6_diagnostic(apps, schema_editor):
    PlacementTest = apps.get_model("exams", "PlacementTest")
    PlacementTest.objects.filter(title="آزمون تشخیصی شروع ششم").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_grade6_diagnostic, remove_grade6_diagnostic),
    ]
