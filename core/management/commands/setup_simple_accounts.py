from getpass import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import ClassRoom, UserProfile
from students.models import StudentProfile


User = get_user_model()


class Command(BaseCommand):
    help = (
        "Create the default demo student and ensure the teacher profile exists. "
        "Existing usernames and passwords are never reset."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--student-username",
            default="student_demo",
            help="Username for the default demo student (default: student_demo).",
        )
        parser.add_argument(
            "--teacher-username",
            default="teacher",
            help="Username for the teacher account (default: teacher).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        teacher_username = options["teacher_username"]
        student_username = options["student_username"]

        teacher = User.objects.filter(username=teacher_username).first()
        if teacher is None:
            password = getpass(f"رمز جدید برای حساب معلم ({teacher_username}): ")
            confirmation = getpass("تکرار رمز معلم: ")
            if not password or password != confirmation:
                raise CommandError("رمز معلم خالی است یا دو رمز یکسان نیستند.")
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
            self.stdout.write(self.style.SUCCESS("حساب معلم ساخته شد."))
        else:
            teacher_profile, created = UserProfile.objects.get_or_create(
                user=teacher,
                defaults={
                    "role": UserProfile.Role.TEACHER,
                    "display_name": "معلم پیچک دانش",
                    "is_active_profile": True,
                },
            )
            if not created and teacher_profile.role != UserProfile.Role.TEACHER:
                self.stdout.write(self.style.WARNING(
                    f"حساب {teacher_username} از قبل وجود دارد و نقش آن "
                    f"{teacher_profile.role!r} است؛ برای حفظ حساب تغییرش ندادم."
                ))
            else:
                self.stdout.write("حساب معلم موجود است؛ رمز آن تغییر نکرد.")

        student = User.objects.filter(username=student_username).first()
        if student is None:
            password = getpass(f"رمز دانش‌آموز پیش‌فرض ({student_username}): ")
            confirmation = getpass("تکرار رمز دانش‌آموز: ")
            if not password or password != confirmation:
                raise CommandError("رمز دانش‌آموز خالی است یا دو رمز یکسان نیستند.")
            student = User.objects.create_user(
                username=student_username,
                password=password,
                first_name="دانش‌آموز",
                last_name="نمونه",
            )
            UserProfile.objects.create(
                user=student,
                role=UserProfile.Role.STUDENT,
                display_name="دانش‌آموز نمونه",
                is_active_profile=True,
            )
            self.stdout.write(self.style.SUCCESS("حساب دانش‌آموز پیش‌فرض ساخته شد."))
        else:
            self.stdout.write("نام کاربری دانش‌آموز پیش‌فرض از قبل وجود دارد؛ رمز آن تغییر نکرد.")

        profile = UserProfile.objects.filter(user=student).first()
        if profile and profile.role != UserProfile.Role.STUDENT:
            self.stdout.write(self.style.WARNING(
                f"حساب {student_username} نقش {profile.role!r} دارد؛ نقش آن تغییر نکرد."
            ))
        else:
            UserProfile.objects.get_or_create(
                user=student,
                defaults={
                    "role": UserProfile.Role.STUDENT,
                    "display_name": "دانش‌آموز نمونه",
                    "is_active_profile": True,
                },
            )
            classroom = ClassRoom.objects.filter(grade=6, is_active=True).order_by("id").first()
            StudentProfile.objects.get_or_create(
                user=student,
                defaults={"grade": 6, "is_free": True, "classroom": classroom},
            )
            self.stdout.write(self.style.SUCCESS(
                f"دانش‌آموز نمونه آماده است: نام کاربری {student_username}"
            ))

        self.stdout.write("")
        self.stdout.write("رمز هیچ حساب موجودی تغییر نکرده است.")
        self.stdout.write("برای ورود به پنل معلم از نام کاربری معلم و رمز فعلی او استفاده کنید.")
