from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from django.forms import ImageField as DjangoImageField
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.utils import timezone

from core.permissions import is_teacher, is_admin
from core.models import ClassRoom, DailyTask, StudentTask
from exams.models import PlacementAttempt, PlacementQuestion, PlacementTest
from students.models import StudentProfile


IQ_TEST_TITLE = "آزمون هوش تصویری پیچک دانش"
IQ_QUESTIONS = [
    {"id":"q1","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="دایره، مربع، دایره، مربع، جای خالی"><circle cx="45" cy="45" r="20" fill="#15966d"/><rect x="100" y="25" width="40" height="40" rx="5" fill="#f2b84b"/><circle cx="195" cy="45" r="20" fill="#15966d"/><rect x="250" y="25" width="40" height="40" rx="5" fill="#f2b84b"/><text x="360" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","دایره سبز"),("B","مربع زرد"),("C","مثلث آبی"),("D","ستاره قرمز")],"answer":"A"},
    {"id":"q2","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="یک نقطه، دو نقطه، سه نقطه، جای خالی"><g fill="#536fe5"><circle cx="45" cy="45" r="7"/><circle cx="130" cy="35" r="7"/><circle cx="130" cy="55" r="7"/><circle cx="215" cy="30" r="7"/><circle cx="215" cy="45" r="7"/><circle cx="215" cy="60" r="7"/></g><text x="320" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","یک نقطه"),("B","دو نقطه"),("C","چهار نقطه"),("D","شش نقطه")],"answer":"C"},
    {"id":"q3","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="مثلث رو به بالا، مثلث رو به پایین، مثلث رو به بالا، جای خالی"><polygon points="45,18 20,65 70,65" fill="#f2b84b"/><polygon points="130,68 105,21 155,21" fill="#15966d"/><polygon points="215,18 190,65 240,65" fill="#f2b84b"/><text x="320" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","مثلث زرد رو به بالا"),("B","مثلث سبز رو به پایین"),("C","دایره سبز"),("D","مربع زرد")],"answer":"B"},
    {"id":"q4","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="مربع کوچک، مربع بزرگ، مربع کوچک، جای خالی"><rect x="27" y="27" width="36" height="36" rx="4" fill="#9b70d6"/><rect x="105" y="12" width="66" height="66" rx="5" fill="#9b70d6"/><rect x="202" y="27" width="36" height="36" rx="4" fill="#9b70d6"/><text x="320" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","مربع کوچک"),("B","مربع بزرگ"),("C","دایره بزرگ"),("D","مثلث کوچک")],"answer":"B"},
    {"id":"q5","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="یک ستاره، دو ستاره، سه ستاره، جای خالی"><g fill="#f2b84b" font-size="30" text-anchor="middle"><text x="45" y="56">★</text><text x="125" y="56">★</text><text x="153" y="56">★</text><text x="215" y="56">★</text><text x="243" y="56">★</text><text x="271" y="56">★</text></g><text x="350" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","دو ستاره"),("B","سه ستاره"),("C","چهار ستاره"),("D","پنج ستاره")],"answer":"C"},
]


def simple_home(request):
    if request.user.is_authenticated:
        if is_teacher(request.user) or is_admin(request.user):
            return redirect("simple-teacher")
        if hasattr(request.user, "student_profile"):
            return redirect("simple-student")
    return render(request, "simple/home.html")


@login_required(login_url="login")
def simple_student(request):
    student = getattr(request.user, "student_profile", None)
    if student is None:
        return redirect("simple-teacher" if is_teacher(request.user) or is_admin(request.user) else "login")

    message = None
    error = None
    if request.method == "POST" and request.POST.get("action") == "submit_task":
        record = get_object_or_404(
            StudentTask.objects.select_related("task"),
            pk=request.POST.get("record_id"),
            student=student,
        )
        if record.status == StudentTask.Status.DONE:
            error = "این فعالیت قبلاً تأیید شده است."
        elif record.status == StudentTask.Status.REVIEW:
            message = "این فعالیت قبلاً برای بررسی معلم فرستاده شده است."
        else:
            record.status = StudentTask.Status.REVIEW
            record.save(update_fields=["status", "updated_at"])
            message = "آفرین! فعالیتت برای بررسی معلم فرستاده شد."

    task_records = StudentTask.objects.filter(
        student=student
    ).select_related("task", "task__classroom").order_by(
        "-task__task_date", "-task_id"
    )
    attempts = PlacementAttempt.objects.filter(student=student).select_related("test")[:5]
    total_tasks = task_records.count()
    completed_tasks = task_records.filter(status=StudentTask.Status.DONE).count()
    waiting_tasks = task_records.filter(status=StudentTask.Status.REVIEW).count()
    pending_tasks = task_records.filter(status=StudentTask.Status.PENDING).count()
    return render(request, "simple/student.html", {
        "student": student,
        "attempts": attempts,
        "task_records": task_records,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "waiting_tasks": waiting_tasks,
        "pending_tasks": pending_tasks,
        "message": message,
        "error": error,
    })


@login_required(login_url="login")
def simple_iq_test(request):
    student = getattr(request.user, "student_profile", None)
    if student is None:
        return redirect("simple-teacher" if is_teacher(request.user) or is_admin(request.user) else "login")
    error = None
    if request.method == "POST":
        answers = {q["id"]: request.POST.get(q["id"], "") for q in IQ_QUESTIONS}
        if any(not value for value in answers.values()):
            error = "لطفاً برای هر پنج سؤال یک پاسخ انتخاب کن."
        else:
            correct = sum(answers[q["id"]] == q["answer"] for q in IQ_QUESTIONS)
            test, _ = PlacementTest.objects.get_or_create(
                title=IQ_TEST_TITLE,
                defaults={"grade": student.grade, "duration_minutes": 8, "is_active": True},
            )
            attempt = PlacementAttempt.objects.create(
                student=student,
                test=test,
                score=round(correct * 100 / len(IQ_QUESTIONS)),
                correct_answers=correct,
                total_questions=len(IQ_QUESTIONS),
                level=max(1, min(10, correct * 2)),
                completed_at=timezone.now(),
            )
            return render(request, "simple/result.html", {"attempt": attempt})
    return render(request, "simple/iq.html", {"questions": IQ_QUESTIONS, "error": error})



@login_required(login_url="login")
def simple_teacher(request):
    if not _can_manage_learning(request.user):
        return redirect("simple-student")

    is_manager = is_admin(request.user) or request.user.is_superuser
    classrooms = ClassRoom.objects.filter(is_active=True)
    if not is_manager:
        classrooms = classrooms.filter(teacher=request.user)

    # Teachers can see unassigned students so they can place them into a class;
    # students already assigned to another teacher remain hidden.
    visible_grades = classrooms.values_list("grade", flat=True).distinct()
    students = StudentProfile.objects.select_related(
        "user", "classroom"
    ).filter(
        Q(classroom__in=classrooms)
        | Q(classroom__isnull=True, grade__in=visible_grades)
    ).order_by("user__first_name", "user__last_name")

    tasks = DailyTask.objects.filter(classroom__in=classrooms).select_related(
        "classroom", "created_by"
    ).annotate(
        assigned_count=Count("student_tasks"),
        completed_count=Count(
            "student_tasks",
            filter=Q(student_tasks__status=StudentTask.Status.DONE),
        ),
    ).order_by("-task_date", "-id")[:6]

    return render(request, "simple/teacher.html", {
        "students": students,
        "student_count": students.count(),
        "classrooms": classrooms,
        "classroom_count": classrooms.count(),
        "task_count": DailyTask.objects.filter(classroom__in=classrooms).count(),
        "pending_count": StudentTask.objects.filter(
            task__classroom__in=classrooms,
            status=StudentTask.Status.PENDING,
        ).count(),
        "review_count": StudentTask.objects.filter(
            task__classroom__in=classrooms,
            status=StudentTask.Status.REVIEW,
        ).count(),
        "tasks": tasks,
    })


def _can_manage_learning(user):
    return bool(
        user.is_authenticated
        and (is_teacher(user) or is_admin(user) or user.is_superuser)
    )


@login_required(login_url="login")
def teacher_student_detail(request, student_id):
    if not _can_manage_learning(request.user):
        return redirect("simple-student")

    queryset = StudentProfile.objects.select_related("user", "classroom")
    if not (is_admin(request.user) or request.user.is_superuser):
        teacher_classes = ClassRoom.objects.filter(teacher=request.user, is_active=True)
        visible_grades = teacher_classes.values_list("grade", flat=True).distinct()
        queryset = queryset.filter(
            Q(classroom__in=teacher_classes)
            | Q(classroom__isnull=True, grade__in=visible_grades)
        )

    student = get_object_or_404(queryset, pk=student_id)
    task_records = StudentTask.objects.filter(
        student=student
    ).select_related("task", "task__classroom").order_by("-updated_at")[:30]
    placement_attempts = PlacementAttempt.objects.filter(
        student=student
    ).select_related("test").order_by("-completed_at")[:10]

    return render(request, "simple/student_detail.html", {
        "student": student,
        "task_records": task_records,
        "placement_attempts": placement_attempts,
    })

@login_required(login_url="login")
def teacher_activities(request):
    if not _can_manage_learning(request.user):
        return redirect("simple-student")

    is_manager = is_admin(request.user) or request.user.is_superuser
    classrooms = ClassRoom.objects.filter(is_active=True)
    if not is_manager:
        classrooms = classrooms.filter(teacher=request.user)

    message = None
    error = None

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "setup_class":
            with transaction.atomic():
                classroom = classrooms.filter(name="ششم ۱", grade=6).first()
                if classroom is None:
                    classroom = ClassRoom.objects.create(
                        name="ششم ۱",
                        grade=6,
                        teacher=request.user,
                        is_active=True,
                    )
                unassigned = StudentProfile.objects.filter(
                    grade=6, classroom__isnull=True
                )
                assigned_count = unassigned.update(classroom=classroom)
            message = f"کلاس ششم ۱ آماده شد و {assigned_count} دانش‌آموز به آن متصل شدند."

        elif action == "create_task":
            classroom_id = request.POST.get("classroom_id")
            classroom = get_object_or_404(classrooms, pk=classroom_id)
            title = request.POST.get("title", "").strip()
            description = request.POST.get("description", "").strip()
            task_date = parse_date(request.POST.get("task_date", ""))
            try:
                max_score = int(request.POST.get("max_score", "20"))
            except (TypeError, ValueError):
                max_score = 0

            if not title:
                error = "عنوان فعالیت را وارد کن."
            elif task_date is None:
                error = "تاریخ فعالیت معتبر نیست."
            elif not 1 <= max_score <= 100:
                error = "امتیاز فعالیت باید بین ۱ تا ۱۰۰ باشد."
            else:
                with transaction.atomic():
                    task = DailyTask.objects.create(
                        classroom=classroom,
                        title=title,
                        description=description,
                        task_date=task_date,
                        max_score=max_score,
                        created_by=request.user,
                    )
                    students_in_class = list(
                        StudentProfile.objects.filter(classroom=classroom)
                    )
                    StudentTask.objects.bulk_create(
                        [StudentTask(task=task, student=student) for student in students_in_class],
                        ignore_conflicts=True,
                    )
                message = f"فعالیت ساخته شد و برای {len(students_in_class)} دانش‌آموز ثبت شد."

        elif action == "review_task":
            record_id = request.POST.get("record_id")
            records = StudentTask.objects.select_related("task", "student")
            if not is_manager:
                records = records.filter(task__classroom__teacher=request.user)
            record = get_object_or_404(records, pk=record_id)
            status = request.POST.get("status", "")
            note = request.POST.get("note", "").strip()[:500]
            score_text = request.POST.get("score", "").strip()

            if status not in StudentTask.Status.values:
                error = "وضعیت انتخاب‌شده معتبر نیست."
            else:
                score = None
                if score_text:
                    try:
                        score = int(score_text)
                    except ValueError:
                        score = -1
                if score is not None and not 0 <= score <= record.task.max_score:
                    error = f"امتیاز باید بین صفر تا {record.task.max_score} باشد."
                else:
                    record.status = status
                    record.score = score
                    record.note = note
                    record.save(update_fields=["status", "score", "note", "updated_at"])
                    message = "عملکرد دانش‌آموز ذخیره شد."

    classrooms = classrooms.order_by("grade", "name")
    tasks = DailyTask.objects.filter(classroom__in=classrooms).select_related(
        "classroom"
    ).annotate(
        assigned_count=Count("student_tasks"),
        completed_count=Count(
            "student_tasks",
            filter=Q(student_tasks__status=StudentTask.Status.DONE),
        ),
    ).order_by("-task_date", "-id")

    records = StudentTask.objects.filter(
        task__classroom__in=classrooms
    ).select_related("student__user", "task", "task__classroom").order_by(
        "-updated_at"
    )[:100]

    return render(request, "simple/activities.html", {
        "classrooms": classrooms,
        "tasks": tasks,
        "records": records,
        "message": message,
        "error": error,
        "today": timezone.localdate(),
    })

@login_required(login_url="login")
def teacher_test_manager(request):
    if not _can_manage_learning(request.user):
        return redirect("simple-student")

    is_manager = is_admin(request.user) or request.user.is_superuser
    if is_manager:
        allowed_grades = None
    else:
        allowed_grades = list(
            ClassRoom.objects.filter(
                teacher=request.user, is_active=True
            ).values_list("grade", flat=True).distinct()
        )

    tests = PlacementTest.objects.all()
    if allowed_grades is not None:
        tests = tests.filter(grade__in=allowed_grades)

    message = None
    error = None
    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "create_test":
            title = request.POST.get("title", "").strip()
            try:
                duration = int(request.POST.get("duration_minutes", "15"))
            except (TypeError, ValueError):
                duration = 15
            if not title:
                error = "عنوان آزمون را بنویس."
            elif not 1 <= duration <= 240:
                error = "زمان آزمون باید بین ۱ تا ۲۴۰ دقیقه باشد."
            elif allowed_grades is not None and 6 not in allowed_grades:
                error = "برای ساخت آزمون، ابتدا کلاس پایه ششم را به حساب معلم متصل کن."
            else:
                test = PlacementTest.objects.create(
                    title=title, grade=6, duration_minutes=duration, is_active=False
                )
                message = f"آزمون «{test.title}» ساخته شد. حالا سؤال اضافه کن."

        elif action in ("add_question", "toggle_test"):
            test = get_object_or_404(tests, pk=request.POST.get("test_id"))
            if action == "toggle_test":
                if not test.is_active and not test.questions.filter(is_active=True).exists():
                    error = "برای فعال‌کردن، ابتدا دست‌کم یک سؤال فعال اضافه کن."
                else:
                    test.is_active = not test.is_active
                    test.save(update_fields=["is_active"])
                    message = "وضعیت آزمون تغییر کرد."
            else:
                question_text = request.POST.get("question_text", "").strip()
                options = [
                    request.POST.get("option_" + letter.lower(), "").strip()
                    for letter in "ABCD"
                ]
                question_image = request.FILES.get("question_image")
                option_images = [
                    request.FILES.get("option_" + letter.lower() + "_image")
                    for letter in "ABCD"
                ]
                correct = request.POST.get("correct_option", "")
                uploads = [("تصویر سؤال", question_image)] + [
                    ("تصویر گزینه " + str(i + 1), upload)
                    for i, upload in enumerate(option_images)
                ]
                try:
                    for label, upload in uploads:
                        if upload:
                            if upload.size > 5 * 1024 * 1024:
                                raise ValidationError(
                                    f"{label}: حجم عکس نباید بیشتر از ۵ مگابایت باشد."
                                )
                            DjangoImageField().clean(upload)
                except ValidationError as exc:
                    error = " ".join(exc.messages)

                if not error and not question_text and not question_image:
                    error = "متن سؤال یا تصویر سؤال را وارد کن."
                elif not error and any(
                    not option and not option_images[i]
                    for i, option in enumerate(options)
                ):
                    error = "برای هر گزینه متن یا تصویر قرار بده."
                elif not error and correct not in ("A", "B", "C", "D"):
                    error = "گزینه درست را انتخاب کن."

                if not error:
                    next_order = (
                        test.questions.order_by("-order").values_list(
                            "order", flat=True
                        ).first() or 0
                    ) + 1
                    PlacementQuestion.objects.create(
                        test=test,
                        text=question_text,
                        question_image=question_image,
                        option_a=options[0],
                        option_a_image=option_images[0],
                        option_b=options[1],
                        option_b_image=option_images[1],
                        option_c=options[2],
                        option_c_image=option_images[2],
                        option_d=options[3],
                        option_d_image=option_images[3],
                        correct_option=correct,
                        order=next_order,
                        is_active=True,
                    )
                    message = "سؤال و تصاویر آن با موفقیت اضافه شد."

        elif action == "toggle_question":
            question = get_object_or_404(
                PlacementQuestion.objects.select_related("test").filter(test__in=tests),
                pk=request.POST.get("question_id"),
            )
            question.is_active = not question.is_active
            question.save(update_fields=["is_active"])
            message = "وضعیت سؤال تغییر کرد."

    tests = tests.prefetch_related("questions").order_by("-id")
    return render(
        request,
        "simple/test_manager.html",
        {"tests": tests, "message": message, "error": error},
    )


@login_required(login_url="login")
def student_test_list(request):
    student = getattr(request.user, "student_profile", None)
    if student is None:
        return redirect(
            "simple-teacher"
            if is_teacher(request.user) or is_admin(request.user)
            else "login"
        )
    tests = (
        PlacementTest.objects.filter(
            is_active=True,
            grade=student.grade,
            questions__is_active=True,
        )
        .distinct()
        .prefetch_related("questions")
        .order_by("-id")
    )
    return render(request, "simple/test_list.html", {"tests": tests})


@login_required(login_url="login")
def student_take_test(request, test_id):
    student = getattr(request.user, "student_profile", None)
    if student is None:
        return redirect(
            "simple-teacher"
            if is_teacher(request.user) or is_admin(request.user)
            else "login"
        )
    test = get_object_or_404(
        PlacementTest, pk=test_id, is_active=True, grade=student.grade
    )
    questions = list(
        test.questions.filter(is_active=True).order_by("order", "id")
    )
    if not questions:
        return redirect("student-test-list")

    error = None
    if request.method == "POST":
        answers = {
            str(question.id): request.POST.get("question_" + str(question.id), "")
            for question in questions
        }
        if any(value not in ("A", "B", "C", "D") for value in answers.values()):
            error = "لطفاً برای همه سؤال‌ها یک گزینه انتخاب کن."
        else:
            correct = sum(
                answers[str(question.id)] == question.correct_option
                for question in questions
            )
            attempt = PlacementAttempt.objects.create(
                student=student,
                test=test,
                score=round(correct * 100 / len(questions)),
                correct_answers=correct,
                total_questions=len(questions),
                level=max(
                    1, min(10, round(correct * 10 / len(questions)))
                ),
                completed_at=timezone.now(),
            )
            return render(
                request,
                "simple/result.html",
                {"attempt": attempt, "custom_test": True},
            )
    return render(
        request,
        "simple/test_take.html",
        {"test": test, "questions": questions, "error": error},
    )

