from django.db import migrations, models


def populate_topics_and_skills(apps, schema_editor):
    PlacementQuestion = apps.get_model("exams", "PlacementQuestion")
    data = {
        1: ("کسرها", "تشخیص کسرهای مساوی"),
        2: ("عدد و چهارعمل اصلی", "جمع اعداد طبیعی"),
        3: ("هندسه و اندازه‌گیری", "محاسبه محیط مربع"),
        4: ("حل مسئله", "حل مسئله ضربی در موقعیت واقعی"),
        5: ("عدد و چهارعمل اصلی", "رعایت ترتیب انجام عملیات"),
        6: ("گیاهان", "شناخت نیازهای اصلی گیاه"),
        7: ("بدن انسان", "شناخت عملکرد اندام‌ها"),
        8: ("مواد و تغییرات", "تشخیص حالت‌های ماده"),
        9: ("نیرو و حرکت", "شناخت نیروی گرانش"),
        10: ("زنجیره غذایی", "تشخیص رابطه تولیدکننده و مصرف‌کننده"),
        11: ("واژگان", "تشخیص واژه هم‌معنی"),
        12: ("دستور زبان", "تشخیص فاعل جمله"),
        13: ("جمله و نگارش", "تشخیص جمله کامل"),
        14: ("املا", "تشخیص شکل درست واژه"),
        15: ("دستور زبان", "تشخیص نقش معنایی واژه در جمله"),
        16: ("جغرافیا", "شناخت جهت‌های اصلی"),
        17: ("جغرافیا", "شناخت جایگاه قاره‌ای ایران"),
        18: ("منابع طبیعی", "تشخیص منبع طبیعی"),
        19: ("زندگی اجتماعی", "شناخت رفتار مناسب برای همکاری"),
        20: ("تاریخ و فرهنگ", "شناخت مفهوم میراث فرهنگی"),
    }

    for question in PlacementQuestion.objects.all():
        topic, skill = data.get(question.order, ("عمومی", "مهارت پایه"))
        question.topic = topic
        question.skill = skill
        question.save(update_fields=["topic", "skill"])


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0002_seed_grade6_diagnostic"),
    ]

    operations = [
        migrations.AddField(
            model_name="placementquestion",
            name="topic",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="placementquestion",
            name="skill",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddIndex(
            model_name="placementquestion",
            index=models.Index(fields=["subject", "topic", "skill"], name="exams_plac_subject_9e6c7a_idx"),
        ),
        migrations.RunPython(populate_topics_and_skills, migrations.RunPython.noop),
    ]
