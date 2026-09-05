import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.models import ClassRoom, UserProfile
from students.models import StudentProfile


def _json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _profile_data(user):
    profile = getattr(user, "profile", None)
    return {
        "id": user.id,
        "username": user.username,
        "name": user.get_full_name() or user.username,
        "role": profile.role if profile else ("admin" if user.is_staff else None),
        "mobile": profile.mobile if profile else None,
        "is_staff": user.is_staff,
    }


@csrf_exempt
def auth_login(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    data = _json_body(request)
    if data is None:
        return JsonResponse({"detail": "Invalid JSON."}, status=400)

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"detail": "نام کاربری یا رمز عبور نادرست است."}, status=401)

    login(request, user)
    return JsonResponse({"user": _profile_data(user)})


def auth_me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False}, status=401)
    return JsonResponse({"authenticated": True, "user": _profile_data(request.user)})


def auth_logout(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)
    logout(request)
    return JsonResponse({"ok": True})


def classrooms_api(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    classes = ClassRoom.objects.filter(is_active=True).select_related("teacher")
    data = [
        {
            "id": item.id,
            "name": item.name,
            "grade": item.grade,
            "academic_year": item.academic_year,
            "teacher_id": item.teacher_id,
            "teacher_name": item.teacher.get_full_name() if item.teacher else None,
        }
        for item in classes
    ]
    return JsonResponse({"results": data})


def students_api(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    students = StudentProfile.objects.select_related("user", "classroom").all()
    data = [
        {
            "id": item.id,
            "user_id": item.user_id,
            "name": item.user.get_full_name() or item.user.username,
            "mobile": item.mobile,
            "grade": item.grade,
            "classroom_id": item.classroom_id,
            "classroom": item.classroom.name if item.classroom else None,
            "points": item.points,
            "level": item.level,
            "streak": item.streak,
        }
        for item in students
    ]
    return JsonResponse({"results": data})


def teachers_api(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    users = UserProfile.objects.filter(role=UserProfile.Role.TEACHER).select_related("user")
    data = [
        {
            "id": profile.user_id,
            "name": profile.user.get_full_name() or profile.user.username,
            "mobile": profile.mobile,
        }
        for profile in users
    ]
    return JsonResponse({"results": data})
