import secrets
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from students.models import StudentProfile

User = get_user_model()

ROSTER = [
    ("ایمان", "ابراهیمی عمارت", "iman01"), ("محمدپارسا", "اکبری فرخانی", "mparsa02"),
    ("سجاد", "الیاسی یوسف‌آباد", "sajad03"), ("امیرمحمد", "ایزی", "amir04"),
    ("کارن", "بابایی", "karen05"), ("مهیار", "بابایی فیروزآباد", "mahyar06"),
    ("امیرعلی", "بیگ‌زاده", "amirali07"), ("محمدمهدی", "جعفری تیکانلو", "mmahdi08"),
    ("امیرعباس", "چوپانی", "amirabbas09"), ("سجاد", "حسن‌زاده خواجه‌ها", "sajad10"),
    ("محمدرضا", "خان‌زاده", "mreza11"), ("سینا", "دام‌آفرین", "sina12"),
    ("سینا یار", "رفیعی کهنه‌رود", "sinayar13"), ("امیرمحمد", "رهنمازوباران", "amirm14"),
    ("علی", "زارعی", "ali15"), ("افشین", "سهرابی‌فر", "afshin16"),
    ("محمدامین", "شاکری", "mamin17"), ("متین", "شریفی", "matin18"),
    ("آرش", "صاحب‌الزمانی", "arsh19"), ("محمد", "صبوری‌پور", "mohammad20"),
    ("پرهام", "صفی‌پور", "parham21"), ("سیدامیرمحمد", "قربانی موسوی", "samir22"),
    ("امیرعباس", "گودرزی", "amirabbas23"), ("محمدمهدی", "محمدی‌زاده", "mmahdi24"),
    ("طاها", "نامی", "taha25"), ("محمدصالحا", "نظری", "msaleha26"),
    ("فرمان", "نوحه‌خوان قوچان عتیق", "farman27"),
] + [(f"دانش‌آموز {i}", "", f"student{i}") for i in range(28, 31)]


def make_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "P!" + "".join(secrets.choice(alphabet) for _ in range(length))


class Command(BaseCommand):
    help = "Prepare 30 student accounts for the visual IQ quiz. Use --reset-passwords to rotate existing passwords."

    def add_arguments(self, parser):
        parser.add_argument("--reset-passwords", action="store_true", help="Reset passwords for existing roster accounts too.")

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options["reset_passwords"]
        self.stdout.write(self.style.WARNING("Keep this terminal output private; it contains student passwords."))
        created, prepared = 0, 0
        for first_name, last_name, username in ROSTER:
            user = User.objects.filter(username=username).first()
            is_new = user is None
            if is_new:
                user = User(username=username, first_name=first_name, last_name=last_name)
                user.set_password(make_password())
                user.save()
                created += 1
                password = user._generated_quiz_password if hasattr(user, "_generated_quiz_password") else None
                # The password is generated below for new accounts as well, to ensure it can be handed to the teacher.
            elif reset or not user.has_usable_password():
                password = make_password()
                user.set_password(password)
                user.save(update_fields=["password"])
            else:
                password = None

            if not is_new:
                changed = []
                if user.first_name != first_name:
                    user.first_name = first_name; changed.append("first_name")
                if user.last_name != last_name:
                    user.last_name = last_name; changed.append("last_name")
                if changed:
                    user.save(update_fields=changed)

            student, was_created = StudentProfile.objects.get_or_create(user=user, defaults={"grade": 6, "is_free": True})
            if was_created:
                created += 1
            if is_new:
                # Re-set the password here so the printed credential matches the stored password.
                password = make_password()
                user.set_password(password)
                user.save(update_fields=["password"])
            prepared += 1
            status = f"رمز موقت: {password}" if password else "رمز فعلی حفظ شد"
            self.stdout.write(f"{prepared:02d}. {first_name} {last_name} | {username} | {status}")
        self.stdout.write(self.style.SUCCESS(f"آماده‌سازی انجام شد: {prepared} حساب بررسی شد؛ {created} مورد جدید ساخته شد."))
        if not reset:
            self.stdout.write(self.style.WARNING("برای چرخاندن رمز همه حساب‌های موجود، فقط در صورت نیاز دستور را با --reset-passwords اجرا کنید."))
