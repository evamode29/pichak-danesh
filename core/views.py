from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.models import ClassRoom
from core.permissions import current_role, is_teacher
from exams.models import PlacementAttempt
from practice.models import PracticeAttempt
from practice.missions import daily_missions
from students.badges import earned_badges
from students.models import StudentProfile


def home(request):
    return render(request, "home.html")


def login_view(request):
    if request.user.is_authenticated:
        role = current_role(request.user)
        if role == "admin":
            return redirect("admin:index")
        if role == "teacher":
            return redirect("teacher-dashboard")
        return redirect("dashboard")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            role = current_role(user)
            if role == "admin":
                return redirect("admin:index")
            if role == "teacher":
                return redirect("teacher-dashboard")
            return redirect("dashboard")
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

        recent_practice = attempts[:5]
        leaderboard = list(StudentProfile.objects.select_related("user").filter(grade=student.grade).order_by("-points", "id")[:10])
        for index, item in enumerate(leaderboard, start=1):
            item.rank = index
            item.is_me = item.pk == student.pk

    return render(request, "dashboard.html", {"role": role, "student": student, "profile": profile, "latest_attempt": latest_attempt, "subject_progress": subject_progress, "recent_practice": recent_practice, "leaderboard": leaderboard, "badges": badges, "missions": missions})


@login_required(login_url="login")
def teacher_dashboard(request):
    if not is_teacher(request.user):
        return redirect("dashboard")

    classrooms = list(
        ClassRoom.objects.filter(teacher=request.user, is_active=True).order_by("grade", "name")
    )
    students = list(
        StudentProfile.objects.filter(classroom__teacher=request.user)
        .select_related("user", "classroom")
        .order_by("classroom__grade", "classroom__name", "user__first_name", "user__last_name")
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

    return render(
        request,
        "teacher/dashboard.html",
        {
            "role": current_role(request.user),
            "classrooms": classrooms,
            "students": student_rows,
            "total_students": len(students),
            "active_students": active_students,
            "total_points": total_points,
            "total_xp": total_xp,
            "average_accuracy": average_accuracy,
        },
    )
