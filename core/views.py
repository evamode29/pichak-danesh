from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.permissions import current_role
from exams.models import PlacementAttempt
from practice.models import PracticeAttempt
from students.models import StudentProfile


def home(request):
    return render(request, "home.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
    student = getattr(request.user, "student_profile", None)
    profile = getattr(request.user, "profile", None)
    latest_attempt = None
    subject_progress = []
    recent_practice = []
    leaderboard = []

    if student:
        latest_attempt = PlacementAttempt.objects.filter(student=student).first()

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
            subject_progress.append(
                {
                    "code": code,
                    "name": name,
                    "icon": subject_icons[code],
                    "total": data["total"],
                    "correct": data["correct"],
                    "points": data["points"],
                    "accuracy": accuracy,
                }
            )

        recent_practice = attempts[:5]

        leaderboard = list(
            StudentProfile.objects.select_related("user")
            .filter(grade=student.grade)
            .order_by("-points", "id")[:10]
        )
        for index, item in enumerate(leaderboard, start=1):
            item.rank = index
            item.is_me = item.pk == student.pk

    return render(
        request,
        "dashboard.html",
        {
            "role": role,
            "student": student,
            "profile": profile,
            "latest_attempt": latest_attempt,
            "subject_progress": subject_progress,
            "recent_practice": recent_practice,
            "leaderboard": leaderboard,
        },
    )
