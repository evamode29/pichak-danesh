from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.permissions import current_role
from exams.models import PlacementAttempt


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
    if student:
        latest_attempt = PlacementAttempt.objects.filter(student=student).first()
    return render(
        request,
        "dashboard.html",
        {
            "role": role,
            "student": student,
            "profile": profile,
            "latest_attempt": latest_attempt,
        },
    )
