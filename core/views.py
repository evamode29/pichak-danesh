from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ClassRoom, UserProfile
from core.permissions import current_role, is_teacher
from exams.models import PlacementAttempt
from practice.models import PracticeAttempt
from practice.missions import daily_missions
from students.badges import earned_badges
from students.models import StudentProfile


def home(request):
    return render(request, "home.html")


def _redirect_after_login(user):
    """Send each account to its application area, based on the application role."""
    profile = UserProfile.objects.filter(user=user).first()
    role = profile.role if profile else None

    if role == UserProfile.Role.ADMIN or (profile is None and (user.is_superuser or user.is_staff)):
        return redirect("admin:index")
    if role == UserProfile.Role.TEACHER:
        return redirect("teacher-dashboard")
    if role == UserProfile.Role.STUDENT or hasattr(user, "student_profile"):
        return redirect("dashboard")

    return redirect("dashboard")


def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return _redirect_after_login(user)
        error = "نام کاربری یا رمز عبور نادرست است."

    return render(request, "login.html", {"error": error})


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

    if student:
        latest_attempt = PlacementAttempt.objects.filter(student=student).first()
        badges = earned_badges(student)
        missions = daily_missions(student)

        subject_names = {
            "math": "ریاضی",
            "science": "علوم",
            "persian": "فارسی",
            "social": "مطالعات اجتماعی",
        }
        subject_icons = {
            "math": "∑",
            "science": "⚗",
            "persian": "آ",
            "social": "🌍",
        }

        attempts = PracticeAttempt.objects.filter(student=student).select_related("question")
        grouped = {}
        for attempt in attempts:
            subject = attempt.question.subject
            if subject not in grouped:
                grouped[subject] = {"total": 0, "correct": 0, "points": 0}
            grouped[subject]["total"] += 1
            grouped[subject]["correct"] += int(attempt.is_correct)
            grouped[subject]["points"] += attempt.points_earned

        for code, name in subject_names.items():
            data = grouped.get(code, {"total": 0, "correct": 0, "points": 0})
            accuracy = round((data["correct"] / data["total"]) * 100) if data["total"] else 0
            subject_progress.append({"code": code, "name": name, "icon": subject_icons[code], "total": data["total"], "correct": data["correct"], "points": data["points"], "accuracy": accuracy})

        if latest_attempt:
            diagnostic_results = list(latest_attempt.diagnostic_results.all())
            topic_rows = []
            for result in diagnostic_results:
                if result.topic:
                    topic_rows.append({
                        "subject": subject_names.get(result.subject, result.subject),
                        "topic": result.topic,
                        "skill": result.skill,
                        "percentage": result.percentage,
                        "correct": result.correct_answers,
                        "total": result.total_questions,
                    })
            weak_topics = sorted(
                [row for row in topic_rows if row["total"] and row["percentage"] < 70],
                key=lambda row: (row["percentage"], -row["total"]),
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

        recent_practice = attempts[:5]
        leaderboard = list(StudentProfile.objects.select_related("user").filter(grade=student.grade).order_by("-points", "id")[:10])
        for index, item in enumerate(leaderboard, start=1):
            item.rank = index
            item.is_me = item.pk == student.pk

    return render(request, "dashboard.html", {
        "role": role,
        "student": student,
        "profile": profile,
        "latest_attempt": latest_attempt,
        "subject_progress": subject_progress,
        "recent_practice": recent_practice,
        "leaderboard": leaderboard,
        "badges": badges,
        "missions": missions,
        "weak_topics": weak_topics,
        "weakest_subject": weakest_subject,
        "diagnostic_hint": diagnostic_hint,
    })


def _teacher_student_queryset(user):
    return StudentProfile.objects.filter(classroom__teacher=user).select_related("user", "classroom")


@login_required(login_url="login")
def teacher_dashboard(request):
    if not is_teacher(request.user):
        return redirect("dashboard")

    classrooms = list(
        ClassRoom.objects.filter(teacher=request.user, is_active=True).order_by("grade", "name")
    )
    students = list(
        _teacher_student_queryset(request.user).order_by("classroom__grade", "classroom__name", "user__first_name", "user__last_name")
    )

    total_points = sum(student.points for student in students)
    total_xp = sum(student.xp for student in students)
    active_students = sum(1 for student in students if student.points > 0 or student.xp > 0)
    average_accuracy = 0

    student_rows = []
    for student in students:
        attempts = PracticeAttempt.objects.filter(student=student)
        total = attempts.count()
        correct = attempts.filter(is_correct=True).count()
        accuracy = round((correct / total) * 100) if total else 0
        average_accuracy += accuracy
        student_rows.append({
            "student": student,
            "attempts": total,
            "correct": correct,
            "accuracy": accuracy,
        })

    if student_rows:
        average_accuracy = round(average_accuracy / len(student_rows))

    return render(request, "teacher/dashboard.html", {"role": current_role(request.user), "classrooms": classrooms, "students": student_rows, "total_students": len(students), "active_students": active_students, "total_points": total_points, "total_xp": total_xp, "average_accuracy": average_accuracy})


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
        rows.append({"student": student, "attempts": total, "correct": correct, "accuracy": round(correct * 100 / total) if total else 0})

    return render(request, "teacher/students.html", {"students": rows, "classrooms": classrooms, "selected_classroom": selected_classroom})


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
        subject_rows.append({"name": name, "total": subject_total, "correct": subject_correct, "accuracy": round(subject_correct * 100 / subject_total) if subject_total else 0})

    latest_placement = PlacementAttempt.objects.filter(student=student).select_related("test", "approved_by").first()

    return render(request, "teacher/student_detail.html", {
        "student": student,
        "attempts": attempts[:12],
        "total_attempts": total,
        "correct_attempts": correct,
        "accuracy": accuracy,
        "subject_rows": subject_rows,
        "badges": earned_badges(student),
        "missions": daily_missions(student),
        "latest_placement": latest_placement,
    })


@login_required(login_url="login")
def teacher_class_detail(request, classroom_id):
    if not is_teacher(request.user):
        return redirect("dashboard")
    classroom = get_object_or_404(ClassRoom, pk=classroom_id, teacher=request.user, is_active=True)
    students = _teacher_student_queryset(request.user).filter(classroom=classroom)
    rows = []
    for student in students.order_by("user__first_name", "user__last_name"):
        attempts = PracticeAttempt.objects.filter(student=student)
        total = attempts.count()
        correct = attempts.filter(is_correct=True).count()
        rows.append({"student": student, "attempts": total, "accuracy": round(correct * 100 / total) if total else 0})
    return render(request, "teacher/class_detail.html", {"classroom": classroom, "rows": rows})
