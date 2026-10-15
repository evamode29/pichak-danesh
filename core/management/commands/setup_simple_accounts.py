import secrets
import string
import unicodedata

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import ClassRoom, UserProfile
from students.models import StudentProfile


User = get_user_model()

# Initial passwords are generated at run time, shown once in the terminal, and
# stored only as Django password hashes. Never commit generated credentials.
STUDENT_NAMES = [
    "ایمان ابراهیمی عمارت",
    "محمدپارسا اکبری فرخانی",
    "سجاد الیاسی یوسف‌آباد",
    "امیرمحمد ایزی",
    "کارن بابایی",
    "مهیار بابائی فیروزآباد",
    "امیرعلی بیگ‌زاده",
    "محمدمهدی جعفری تیکانلو",
    "امیرعباس چوپانی",
    "سجاد حسن‌زاده خواجه‌ها",
    "محمدرضا خان‌زاده",
    "سینا دام‌آفرین",
    "سانیار رفیعی کهنه‌رود",
    "امیرمحمد رهنمازوباران",
    "علی زارعی",
    "افشین سهرابی‌فر",
    "محمدامین شاکری",
    "متین شریفی",
    "آرش صاحب‌الزمانی",
    "محمد صبوری‌پور",
    "پرهام صفی‌پور",
    "سیدامیرمحمد قربانی موسوی",
    "امیرعباس گودرزی",
    "محمدمهدی محمدی‌زاده",
    "طاها نامی",
    "محمدصدرا نظری",
    "فرحان نوحه‌خوان قوچان عتیق",
    "فرحان دوست‌محمدی",
    "کیاراد ذاکر عباسی",
]


def normalize_name(value):
    value = unicodedata.normalize("NFKC", value or "")
    value = "".join(value.replace("\u200c", "").replace("\u200f", "").split())
    return value.replace("ي", "ی").replace("ك", "ک")


def temporary_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def unique_username(base):
    username = base
    suffix = 2
    while User.objects.filter(username=username).exists():
        username = f"{base}_{suffix}"
        suffix += 1
    return username


class Command(BaseCommand):
    help = (
        "Safely prepare teacher/demo accounts and the class roster. Existing "
        "users and passwords are preserved; new student passwords are generated "
        "and printed once to the terminal."
    )

    def add_arguments(self, parser):
        parser.add_argument("--teacher-username", default="teacher")
        parser.add_argument("--demo-username", default="student_demo")
        parser.add_argument(
            "--roster-only",
            action="store_true",
            help="Create or match roster accounts without preparing teacher/demo accounts.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        classroom = ClassRoom.objects.filter(grade=6, is_active=True).order_by("id").first()
        credentials = []
        created_count = 0
        matched_count = 0
        skipped_count = 0

        if not options["roster_only"]:
            teacher_username = options["teacher_username"]
            teacher = User.objects.filter(username=teacher_username).first()
            if teacher is None:
                password = temporary_password(14)
                teacher = User.objects.create_user(
                    username=teacher_username,
                    password=password,
                    first_name="معلم",
                    last_name="پیچک دانش",
                )
                UserProfile.objects.create(
                    user=teacher,
                    role=UserProfile.Role.TEACHER,
                    display_name="معلم پیچک دانش",
                    is_active_profile=True,
                )
                credentials.append(("حساب معلم", teacher_username, password))
                self.stdout.write(self.style.SUCCESS("حساب معلم جدید ساخته شد."))
            else:
                profile, created = UserProfile.objects.get_or_create(
                    user=teacher,
                    defaults={
                        "role": UserProfile.Role.TEACHER,
                        "display_name": "معلم پیچک دانش",
                        "is_active_profile": True,
                    },
                )
                if not created and profile.role != UserProfile.Role.TEACHER:
                    self.stdout.write(self.style.WARNING(
                        f"حساب {teacher_username} از قبل وجود دارد اما نقش آن {profile.role!r} است؛ تغییری ندادم."
                    ))
                else:
                    self.stdout.write("حساب معلم موجود است؛ رمز و نقش موجود تغییر نکرد.")

            demo_username = options["demo_username"]
            demo = User.objects.filter(username=demo_username).first()
            if demo is None:
                password = temporary_password()
                demo = User.objects.create_user(
                    username=demo_username,
                    password=password,
                    first_name="دانش‌آموز",
                    last_name="نمونه",
                )
                UserProfile.objects.create(
                    user=demo,
                    role=UserProfile.Role.STUDENT,
                    display_name="دانش‌آموز نمونه",
                    is_active_profile=True,
                )
                StudentProfile.objects.get_or_create(
                    user=demo,
                    defaults={"grade": 6, "is_free": True, "classroom": classroom},
                )
                credentials.append(("دانش‌آموز نمونه", demo_username, password))
                self.stdout.write(self.style.SUCCESS("حساب دانش‌آموز پیش‌فرض ساخته شد."))
            else:
                self.stdout.write("حساب دانش‌آموز پیش‌فرض موجود است؛ رمز آن تغییر نکرد.")

        existing_users = list(User.objects.all().only("id", "username", "first_name", "last_name"))
        users_by_name = {}
        for user in existing_users:
            key = normalize_name(f"{user.first_name} {user.last_name}")
            if key:
                users_by_name.setdefault(key, []).append(user)

        for index, full_name in enumerate(STUDENT_NAMES, start=1):
            first_name, _, last_name = full_name.partition(" ")
            key = normalize_name(full_name)
            matches = users_by_name.get(key, [])
            student_user = next(
                (user for user in matches if StudentProfile.objects.filter(user=user).exists()),
                None,
            )

            if student_user is not None:
                profile = UserProfile.objects.filter(user=student_user).first()
                if profile and profile.role != UserProfile.Role.STUDENT:
                    self.stdout.write(self.style.WARNING(
                        f"ردیف {index}: {full_name} به حسابی با نقش {profile.role!r} متصل است؛ دست نزدم."
                    ))
                    skipped_count += 1
                    continue
                UserProfile.objects.get_or_create(
                    user=student_user,
                    defaults={
                        "role": UserProfile.Role.STUDENT,
                        "display_name": full_name,
                        "is_active_profile": True,
                    },
                )
                matched_count += 1
                continue

            candidate = matches[0] if matches else None
            if candidate:
                existing_profile = UserProfile.objects.filter(user=candidate).first()
                if existing_profile and existing_profile.role != UserProfile.Role.STUDENT:
                    self.stdout.write(self.style.WARNING(
                        f"ردیف {index}: نام {full_name} با حساب غیر دانش‌آموزی تطبیق دارد؛ حساب جدید نساختم."
                    ))
                    skipped_count += 1
                    continue
                UserProfile.objects.get_or_create(
                    user=candidate,
                    defaults={
                        "role": UserProfile.Role.STUDENT,
                        "display_name": full_name,
                        "is_active_profile": True,
                    },
                )
                StudentProfile.objects.get_or_create(
                    user=candidate,
                    defaults={"grade": 6, "is_free": True, "classroom": classroom},
                )
                matched_count += 1
                continue

            username = unique_username(f"pichak{index:03d}")
            password = temporary_password()
            student_user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            UserProfile.objects.create(
                user=student_user,
                role=UserProfile.Role.STUDENT,
                display_name=full_name,
                is_active_profile=True,
            )
            StudentProfile.objects.create(
                user=student_user,
                grade=6,
                is_free=True,
                classroom=classroom,
            )
            credentials.append((full_name, username, password))
            users_by_name.setdefault(key, []).append(student_user)
            created_count += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"پایان: {created_count} حساب دانش‌آموز جدید، {matched_count} حساب موجود تطبیق داده شد، {skipped_count} مورد به‌علت نقش متعارض رد شد."
        ))
        if credentials:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING(
                "رمزهای موقت حساب‌های تازه‌ساخته‌شده (فقط همین بار نمایش داده می‌شوند؛ فهرست را امن نگه دارید):"
            ))
            self.stdout.write("نام دانش‌آموز/حساب\tنام کاربری\tرمز موقت")
            for name, username, password in credentials:
                self.stdout.write(f"{name}\t{username}\t{password}")
        else:
            self.stdout.write("حساب تازه‌ای ساخته نشد؛ رمز حساب‌های موجود قابل بازیابی نیست و تغییر هم نکرد.")
        self.stdout.write("")
        self.stdout.write("اگر کلاس فعال پایه ششم وجود نداشته باشد، دانش‌آموزان بدون کلاس ساخته می‌شوند.")
