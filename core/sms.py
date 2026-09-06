import json
import os
from urllib.request import Request, urlopen


class SmsError(Exception):
    pass


def normalize_mobile(value):
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if digits.startswith("0098"):
        digits = digits[4:]
    elif digits.startswith("98") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("9") and len(digits) == 10:
        digits = "0" + digits
    if len(digits) != 11 or not digits.startswith("09"):
        raise SmsError("شماره همراه معتبر نیست.")
    return digits


def send_sms(mobile, message):
    url = os.getenv("SMS_API_URL", "").strip()
    api_key = os.getenv("SMS_API_KEY", "").strip()
    sender = os.getenv("SMS_SENDER", "").strip()
    if not url or not api_key:
        raise SmsError("سرویس پیامک هنوز در تنظیمات سرور فعال نشده است.")

    payload = {"to": mobile, "message": message}
    if sender:
        payload["sender"] = sender
    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            if response.status >= 300:
                raise SmsError("ارسال پیامک ناموفق بود.")
    except Exception as exc:
        if isinstance(exc, SmsError):
            raise
        raise SmsError("ارتباط با سرویس پیامک برقرار نشد.") from exc
