from django.db import migrations


def seed_topics(apps, schema_editor):
    PlacementTest = apps.get_model("exams", "PlacementTest")
    PlacementQuestion = apps.get_model("exams", "PlacementQuestion")
    test = PlacementTest.objects.filter(title="آزمون تشخیصی شروع ششم").first()
    if not test:
        return

    tags = {
        1: ("کسرها", "تشخیص کسرهای مساوی"),
        2: ("عدد و عملیات", "جمع اعداد طبیعی"),
        3: ("هندسه", "محاسبه محیط مربع"),
        4: ("عدد و عملیات", "حل مسئله ضرب"),
        5: ("عدد و عملیات", "رعایت ترتیب عملیات"),
        6: ("گیاهان", "نیازهای اصلی گیاه"),
        7: ("بدن انسان", "شناخت وظیفه اندام‌ها"),
        8: ("مواد و تغییرات", "تشخیص حالت‌های ماده"),
        9: ("نیرو و حرکت", "شناخت نیروی گرانش"),
        10: ("زنجیره غذایی", "تشخیص روابط تغذیه‌ای"),
        11: ("واژگان", "تشخیص واژه هم‌معنی"),
        12: ("دستور زبان", "تشخیص فاعل"),
        13: ("جمله‌سازی", "تشخیص جمله کامل"),
        14: ("املا", "تشخیص شکل درست واژه"),
        15: ("دستور زبان", "تشخیص نقش معنایی واژه"),
        16: ("جغرافیا", "شناخت جهت‌های اصلی"),
        17: ("جغرافیا", "شناخت جایگاه قاره‌ای ایران"),
        18: ("منابع طبیعی", "تشخیص منابع طبیعی"),
        19: ("زندگی اجتماعی", "تشخیص رفتار مشارکتی"),
        20: ("میراث فرهنگی", "شناخت مفهوم میراث فرهنگی"),
    }
    for order, (topic, skill) in tags.items():
        PlacementQuestion.objects.filter(test=test, order=order).update(topic=topic, skill=skill)


def reverse_topics(apps, schema_editor):
    PlacementTest = apps.get_model("exams", "PlacementTest")
    PlacementQuestion = apps.get_model("exams", "PlacementQuestion")
    test = PlacementTest.objects.filter(title="آزمون تشخیصی شروع ششم").first()
    if test:
        PlacementQuestion.objects.filter(test=test).update(topic="", skill="")


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0003_placementdiagnosticresult"),
    ]

    operations = [
        migrations.RunPython(seed_topics, reverse_topics),
    ]
