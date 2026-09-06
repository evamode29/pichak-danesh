from django.http import JsonResponse

from core.models import UserProfile


def current_role(user):
    if not user.is_authenticated:
        return None

    # The explicit application role takes priority over Django's staff flag.
    # This prevents teacher accounts from being redirected to Django admin.
    profile = getattr(user, "profile", None)
    if profile and profile.role:
        return profile.role

    # Only users without a profile fall back to Django's admin flags.
    if user.is_superuser or user.is_staff:
        return UserProfile.Role.ADMIN

    return None


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
