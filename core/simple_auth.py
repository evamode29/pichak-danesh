from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from core.models import UserProfile
from students.models import StudentProfile

User = get_user_model()


def _user_for_identifier(identifier):
    identifier = (identifier or "").strip()
    if not identifier:
        return None

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
            profile = UserProfile.objects.filter(user=authenticated).first()
            if (
                authenticated.is_superuser
                or authenticated.is_staff
                or (profile and profile.role in (UserProfile.Role.ADMIN, UserProfile.Role.TEACHER))
            ):
                return redirect("simple-teacher")
            return redirect("simple-student")
        error = "نام کاربری یا رمز عبور نادرست است."

    from django.shortcuts import render
    return render(request, "login.html", {"error": error})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")
