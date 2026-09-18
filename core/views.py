from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string

from core.models import ClassRoom, UserProfile
from core.permissions import current_role, is_teacher
from exams.models import PlacementAttempt, PlacementQuestion
from practice.models import PracticeAttempt, PracticeQuestion
from practice.adaptive import SUBJECT_NAMES, practice_subject_scores, recommended_subject, subject_label
from practice.missions import daily_missions
from students.badges import earned_badges
from students.models import StudentProfile
from subscriptions.models import Content, Product, Purchase, Subscription, SubscriptionPlan


User = get_user_model()


def home(request):
    return render(request, "home.html")


def _redirect_after_login(user):
    profile = UserProfile.objects.filter(user=user).first()
    role = profile.role if profile else None

    if role == UserProfile.Role.ADMIN or (profile is None and (user.is_superuser or user.is_staff)):
        return redirect("admin:index")
    if role == UserProfile.Role.TEACHER:
        return redirect("teacher-dashboard")
    if role == UserProfile.Role.CONTENT_MANAGER:
        return redirect("content-dashboard")
    if role == UserProfile.Role.STUDENT or hasattr(user, "student_profile"):
        return redirect("dashboard")
    return redirect("dashboard")


def _user_for_identifier(identifier):
    identifier = identifier.strip()
    profile = UserProfile.objects.filter(mobile=identifier).select_related("user").first()
    if profile:
        return profile.user
    student = StudentProfile.objects.filter(mobile=identifier).select_related("user").first()
    if student:
        return student.user
    return User.objects.filter(username=identifier).first()


def login_view(request):
    error = None
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")
        user = _user_for_identifier(identifier)
        authenticated = authenticate(request, username=user.username, password=password) if user else None
        if authenticated is not None:
            login(request, authenticated)
            return _redirect_after_login(authenticated)
        error = "شماره موبایل یا نام کاربری، یا رمز ثابت نادرست است."
    return render(request, "login.html", {"error": error})


def register_view(request):
    error = None
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        requested_username = request.POST.get("username", "").strip()
        if not first_name or not mobile:
            error = "نام و شماره موبایل را وارد کنید."
        elif UserProfile.objects.filter(mobile=mobile).exists() or StudentProfile.objects.filter(mobile=mobile).exists():
            error = "این شماره موبایل قبلاً ثبت شده است. از گزینه ورود استفاده کنید."
        elif requested_username and (
            len(requested_username) < 4
            or len(requested_username) > 30
            or not requested_username.replace("_", "").replace("-", "").isalnum()
        ):
            error = "نام کاربری باید ۴ تا ۳۰ کاراکتر و فقط شامل حروف انگلیسی، عدد، _ یا - باشد."
        elif requested_username and User.objects.filter(username__iexact=requested_username).exists():
            error = "این نام کاربری قبلاً استفاده شده است. یک نام دیگر انتخاب کنید."
        else:
            username = requested_username or f"student_{mobile.lstrip('+').replace(' ', '').replace('-', '')}"
            if User.objects.filter(username=username).exists():
                username = f"student_{mobile[-8:]}"
            if User.objects.filter(username=username).exists():
                error = "این حساب از قبل وجود دارد. از گزینه ورود استفاده کنید."
            else:
                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                )
                UserProfile.objects.create(
                    user=user,
                    role=UserProfile.Role.STUDENT,
                    mobile=mobile,
                    display_name=f"{first_name} {last_name}".strip(),
                )
                StudentProfile.objects.create(
                    user=user,
                    mobile=mobile,
                    grade=6,
                )
                login(request, user)
                return redirect("dashboard")
    return render(request, "register.html", {"error": error})


@login_required(login_url="login")
def fixed_password(request):
    if not hasattr(request.user, "student_profile"):
        return redirect("dashboard")

    error = None
    generated = request.session.pop("new_fixed_password", None)

    if request.method == "POST":
        password = request.POST.get("password", "").strip()
        password2 = request.POST.get("password2", "").strip()
        if password != password2:
            error = "دو رمز عبور یکسان نیستند."
        else:
            try:
                validate_password(password, request.user)
            except ValidationError as exc:
                error = " ".join(exc.messages)
            else:
                request.user.set_password(password)
                request.user.save(update_fields=["password"])
                login(request, request.user)
                return redirect("dashboard")

    return render(request, "account/fixed_password.html", {
        "error": error,
        "generated": generated,
        "has_password": request.user.has_usable_password(),
    })


@login_required(login_url="login")
def generate_fixed_password(request):
    if not hasattr(request.user, "student_profile"):
        return redirect("dashboard")
    if request.method != "POST":
        return redirect("fixed-password")

    password = get_random_string(10, allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789")
    request.user.set_password(password)
    request.user.save(update_fields=["password"])
    request.session["new_fixed_password"] = password
    login(request, request.user)
    return redirect("fixed-password")


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("home")


@login_required(login_url="login")
def dashboard(request):
    role = current_role(request.user)
    if role == "admin":
        return redirect("admin:index")
    if is_teacher(request.user):
        return redirect("teacher-dashboard")
    if role == UserProfile.Role.CONTENT_MANAGER:
        return redirect("content-dashboard")

    student = getattr(request.user, "student_profile", None)
    profile = getattr(request.user, "profile", None)
    latest_attempt = None
    subject_progress = []
    recent_practice = []
    leaderboard = []
    badges = []
    missions = []
    weak_topics = []
    weakest_subject = None
    diagnostic_hint = None
    active_subscription = None
    subscription_products = []
    subscription_plans = []

    if student:
        latest_attempt = PlacementAttempt.objects.filter(student=student).first()
        badges = earned_badges(student)
        missions = daily_missions(student)
        active_subscription = Subscription.active_for(request.user)
        subscription_products = list(Product.objects.filter(
            product_type=Product.ProductType.SUBSCRIPTION, is_active=True
        ).order_by("price", "id")[:3])
        subscription_plans = list(SubscriptionPlan.objects.filter(
            is_active=True, product__is_active=True,
            product__product_type=Product.ProductType.SUBSCRIPTION
        ).select_related("product").order_by("price", "duration_days", "id")[:3])

        subject_names = {"math": "ریاضی", "science": "علوم", "persian": "فارسی", "social": "مطالعات اجتماعی"}
        subject_icons = {"math": "∑", "science": "⚗", "persian": "آ", "social": "🌍"}

        attempts = PracticeAttempt.objects.filter(student=student).select_related("question")
        grouped = {}
        for attempt in attempts:
            subject = attempt.question.subject
            grouped.setdefault(subject, {"total": 0, "correct": 0, "points": 0})
            grouped[subject]["total"] += 1
            grouped[subject]["correct"] += int(attempt.is_correct)
            grouped[subject]["points"] += attempt.points_earned

        for code, name in subject_names.items():
            data = grouped.get(code, {"total": 0, "correct": 0, "points": 0})
            accuracy = round((data["correct"] / data["total"]) * 100) if data["total"] else 0
            subject_progress.append({
                "code": code, "name": name, "icon": subject_icons[code],
                "total": data["total"], "correct": data["correct"],
                "points": data["points"], "accuracy": accuracy
            })

        if latest_attempt:
            diagnostic_results = list(latest_attempt.diagnostic_results.all())
            topic_rows = []
            for result in diagnostic_results:
                if result.topic:
                    topic_rows.append({
                        "subject": subject_names.get(result.subject, result.subject),
                        "topic": result.topic, "skill": result.skill,
                        "percentage": result.percentage,
                        "correct": result.correct_answers, "total": result.total_questions
                    })
            weak_topics = sorted(
                [row for row in topic_rows if row["total"] and row["percentage"] < 70],
                key=lambda row: (row["percentage"], -row["total"])
            )[:3]
            subject_scores = []
            for code, name in subject_names.items():
                rows = [r for r in diagnostic_results if r.subject == code]
                total = sum(r.total_questions for r in rows)
                correct = sum(r.correct_answers for r in rows)
                if total:
                    subject_scores.append((round(correct * 100 / total), name))
            if subject_scores:
                weakest_subject = min(subject_scores, key=lambda item: item[0])
            if weak_topics:
                first = weak_topics[0]
                diagnostic_hint = f"پیشنهاد امروز: مرور {first['topic']} در {first['subject']}"
            elif weakest_subject:
                diagnostic_hint = f"پیشنهاد امروز: چند تمرین بیشتر در {weakest_subject[1]}"

        practice_scores = practice_subject_scores(student)
        placement_focus = weakest_subject[0] if weakest_subject else None
        adaptive_focus = recommended_subject(student, placement_focus)
        if adaptive_focus:
            focus_score = practice_scores.get(adaptive_focus)
            if focus_score:
                diagnostic_hint = (
                    f"پیشنهاد هوشمند امروز: تمرین {subject_label(adaptive_focus)} "
                    f"با دقت فعلی {focus_score['accuracy']}٪"
                )
            elif not diagnostic_hint:
                diagnostic_hint = f"پیشنهاد هوشمند امروز: تمرین {subject_label(adaptive_focus)}"

        recent_practice = attempts[:5]
        leaderboard = list(StudentProfile.objects.select_related("user").filter(
            grade=student.grade).order_by("-points", "id")[:10])
        for index, item in enumerate(leaderboard, start=1):
            item.rank = index
            item.is_me = item.pk == student.pk

    return render(request, "dashboard.html", {
        "role": role, "student": student, "profile": profile, "latest_attempt": latest_attempt,
        "subject_progress": subject_progress, "recent_practice": recent_practice, "leaderboard": leaderboard,
        "badges": badges, "missions": missions, "weak_topics": weak_topics,
        "weakest_subject": weakest_subject, "diagnostic_hint": diagnostic_hint,
        "active_subscription": active_subscription, "subscription_products": subscription_products,
        "subscription_plans": subscription_plans,
    })


def _teacher_student_queryset(user):
    return StudentProfile.objects.filter(classroom__teacher=user).select_related("user", "classroom")


@login_required(login_url="login")
def teacher_dashboard(request):
    if not is_teacher(request.user):
        return redirect("dashboard")
    classrooms = list(ClassRoom.objects.filter(teacher=request.user, is_active=True).order_by("grade", "name"))
    students = list(_teacher_student_queryset(request.user).order_by(
        "classroom__grade", "classroom__name", "user__first_name", "user__last_name"))
    total_points = sum(student.points for student in students)
    total_xp = sum(student.xp for student in students)
    active_students = sum(1 for student in students if student.points > 0 or student.xp > 0)
    student_rows = []
    accuracy_total = 0
    for student in students:
        attempts = PracticeAttempt.objects.filter(student=student)
        total = attempts.count()
        correct = attempts.filter(is_correct=True).count()
        accuracy = round((correct / total) * 100) if total else 0
        accuracy_total += accuracy
        student_rows.append({"student": student, "attempts": total, "correct": correct, "accuracy": accuracy})
    average_accuracy = round(accuracy_total / len(student_rows)) if student_rows else 0
    roster_names = [
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
    ]
    by_username = {row["student"].user.username: row for row in student_rows}
    roster = []
    for index, (first_name, last_name, username) in enumerate(roster_names, start=1):
        row = by_username.get(username)
        roster.append({"number": index, "name": f"{first_name} {last_name}", "username": username,
            "row": row, "status": "active" if row else "ready"})
    for index in range(28, 31):
        roster.append({"number": index, "name": f"ظرفیت خالی {index - 27}", "username": "",
            "row": None, "status": "empty"})
    return render(request, "teacher/dashboard.html", {
        "role": current_role(request.user), "classrooms": classrooms, "students": student_rows,
        "roster": roster, "total_students": len(students), "roster_total": 30,
        "named_students": 27, "empty_slots": 3, "active_students": active_students,
        "total_points": total_points, "total_xp": total_xp, "average_accuracy": average_accuracy,
    })


@login_required(login_url="login")
def teacher_students(request):
    if not is_teacher(request.user):
        return redirect("dashboard")
    classroom_id = request.GET.get("classroom")
    students = _teacher_student_queryset(request.user)
    classrooms = ClassRoom.objects.filter(teacher=request.user, is_active=True).order_by("grade", "name")
    selected_classroom = None
    if classroom_id:
        selected_classroom = get_object_or_404(classrooms, pk=classroom_id)
        students = students.filter(classroom=selected_classroom)
    rows = []
    for student in students.order_by("classroom__grade", "classroom__name", "user__first_name", "user__last_name"):
        attempts = PracticeAttempt.objects.filter(student=student)
        total = attempts.count()
        correct = attempts.filter(is_correct=True).count()
        rows.append({"student": student, "attempts": total, "correct": correct,
            "accuracy": round(correct * 100 / total) if total else 0})
    return render(request, "teacher/students.html", {
        "students": rows, "classrooms": classrooms, "selected_classroom": selected_classroom})


@login_required(login_url="login")
def teacher_student_detail(request, student_id):
    if not is_teacher(request.user):
        return redirect("dashboard")
    student = get_object_or_404(_teacher_student_queryset(request.user), pk=student_id)
    attempts = PracticeAttempt.objects.filter(student=student).select_related("question").order_by("-id")
    total = attempts.count()
    correct = attempts.filter(is_correct=True).count()
    accuracy = round(correct * 100 / total) if total else 0
    subject_names = {"math": "ریاضی", "science": "علوم", "persian": "فارسی", "social": "مطالعات اجتماعی"}
    subject_rows = []
    for code, name in subject_names.items():
        subject_attempts = attempts.filter(question__subject=code)
        subject_total = subject_attempts.count()
        subject_correct = subject_attempts.filter(is_correct=True).count()
        subject_rows.append({"name": name, "total": subject_total, "correct": subject_correct,
            "accuracy": round(subject_correct * 100 / subject_total) if subject_total else 0})
    latest_placement = PlacementAttempt.objects.filter(student=student).select_related("test", "approved_by").first()
    return render(request, "teacher/student_detail.html", {
        "student": student, "attempts": attempts[:12], "total_attempts": total,
        "correct_attempts": correct, "accuracy": accuracy, "subject_rows": subject_rows,
        "badges": earned_badges(student), "missions": daily_missions(student),
        "latest_placement": latest_placement})


@login_required(login_url="login")
def teacher_class_detail(request, classroom_id):
    if not is_teacher(request.user):
        return redirect("dashboard")
    classroom = get_object_or_404(ClassRoom, pk=classroom_id, teacher=request.user, is_active=True)
    students = list(_teacher_student_queryset(request.user).filter(classroom=classroom).order_by(
        "user__first_name", "user__last_name"))
    rows = []
    for student in students:
        attempts = PracticeAttempt.objects.filter(student=student)
        total = attempts.count()
        correct = attempts.filter(is_correct=True).count()
        rows.append({"student": student, "attempts": total, "correct": correct,
            "accuracy": round(correct * 100 / total) if total else 0})
    return render(request, "teacher/class_detail.html", {"classroom": classroom, "students": rows})


@login_required(login_url="login")
def content_dashboard(request):
    if current_role(request.user) != UserProfile.Role.CONTENT_MANAGER:
        return redirect("dashboard")
    question_count = PracticeQuestion.objects.count()
    active_questions = PracticeQuestion.objects.filter(is_active=True).count()
    placement_questions = PlacementQuestion.objects.count()
    total_content = Content.objects.count()
    published_content = Content.objects.filter(is_published=True).count()
    active_products = Product.objects.filter(is_active=True).count()
    subscription_plans = SubscriptionPlan.objects.filter(is_active=True, product__is_active=True).count()
    recent_content = list(Content.objects.select_related("product").order_by("-created_at", "-id")[:8])
    return render(request, "content/dashboard.html", {
        "question_count": question_count, "active_questions": active_questions,
        "placement_questions": placement_questions, "total_content": total_content,
        "published_content": published_content, "active_products": active_products,
        "subscription_plans": subscription_plans, "recent_content": recent_content,
    })
