from django.http import JsonResponse

from core.models import UserProfile


def current_role(user):
    if not user.is_authenticated:
        return None
    if user.is_staff or user.is_superuser:
        return UserProfile.Role.ADMIN
    profile = getattr(user, "profile", None)
    return profile.role if profile else None


def is_admin(user):
    return current_role(user) == UserProfile.Role.ADMIN


def is_teacher(user):
    return current_role(user) == UserProfile.Role.TEACHER


def is_parent(user):
    return current_role(user) == UserProfile.Role.PARENT


def is_student(user):
    return current_role(user) == UserProfile.Role.STUDENT


def require_authenticated(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "احراز هویت الزامی است."}, status=401)
    return None


def require_roles(request, *roles):
    error = require_authenticated(request)
    if error:
        return error
    if current_role(request.user) not in roles:
        return JsonResponse({"detail": "شما دسترسی لازم را ندارید."}, status=403)
    return None
