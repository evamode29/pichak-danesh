import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from core.models import UserProfile
from core.sms import SmsError, normalize_mobile, send_sms
from students.models import StudentProfile

User = get_user_model()
OTP_TTL_SECONDS = 120
OTP_MAX_ATTEMPTS = 5


def otp_request(request):
    error = None
    if request.method == "POST":
        try:
            mobile = normalize_mobile(request.POST.get("mobile"))
            now = timezone.now()
            last_sent = request.session.get("otp_sent_at")
            if last_sent and now.timestamp() - float(last_sent) < 45:
                error = "لطفاً چند ثانیه صبر کنید و دوباره تلاش کنید."
            else:
                code = f"{secrets.randbelow(1_000_000):06d}"
                send_sms(mobile, f"کد ورود پیچک دانش: {code}\nاعتبار: {OTP_TTL_SECONDS // 60} دقیقه")
                request.session["otp_mobile"] = mobile
                request.session["otp_code"] = code
                request.session["otp_sent_at"] = now.timestamp()
                request.session["otp_attempts"] = 0
                return redirect("otp-verify")
        except SmsError as exc:
            if settings.DEBUG and request.POST.get("allow_dev") == "1":
                mobile = normalize_mobile(request.POST.get("mobile"))
                code = "123456"
                request.session["otp_mobile"] = mobile
                request.session["otp_code"] = code
                request.session["otp_sent_at"] = timezone.now().timestamp()
                request.session["otp_attempts"] = 0
                return redirect("otp-verify")
            error = str(exc)

    return render(request, "otp/request.html", {"error": error})


def otp_verify(request):
    mobile = request.session.get("otp_mobile")
    sent_at = request.session.get("otp_sent_at")
    if not mobile or not sent_at:
        return redirect("otp-request")

    error = None
    if timezone.now().timestamp() - float(sent_at) > OTP_TTL_SECONDS:
        request.session.pop("otp_code", None)
        error = "کد منقضی شده است."
        return render(request, "otp/verify.html", {"mobile": mobile, "error": error, "expired": True})

    if request.method == "POST":
        attempts = int(request.session.get("otp_attempts", 0))
        if attempts >= OTP_MAX_ATTEMPTS:
            error = "تعداد تلاش‌ها تمام شده است. دوباره کد دریافت کنید."
        else:
            code = request.POST.get("code", "").strip()
            request.session["otp_attempts"] = attempts + 1
            if secrets.compare_digest(code, str(request.session.get("otp_code", ""))):
                with transaction.atomic():
                    profile = UserProfile.objects.filter(mobile=mobile).select_related("user").first()
                    if profile:
                        user = profile.user
                    else:
                        student_profile = StudentProfile.objects.filter(mobile=mobile).select_related("user").first()
                        if student_profile:
                            user = student_profile.user
                            profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"mobile": mobile})
                            if not profile.mobile:
                                profile.mobile = mobile
                                profile.save(update_fields=["mobile"])
                        else:
                            username = f"student_{mobile[1:]}"
                            user = User.objects.create_user(username=username)
                            profile = UserProfile.objects.create(user=user, role=UserProfile.Role.STUDENT, mobile=mobile, display_name="دانش‌آموز پیچک دانش")
                            StudentProfile.objects.create(user=user, mobile=mobile, grade=6)
                login(request, user)
                for key in ("otp_mobile", "otp_code", "otp_sent_at", "otp_attempts"):
                    request.session.pop(key, None)
                return redirect("dashboard")
            error = "کد واردشده صحیح نیست."

    return render(request, "otp/verify.html", {"mobile": mobile, "error": error, "expired": False})
