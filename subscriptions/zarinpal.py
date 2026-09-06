import json
import urllib.error
import urllib.request

from django.conf import settings


class ZarinpalError(Exception):
    pass


def _request(path, payload):
    base = getattr(settings, "ZARINPAL_API_BASE", "https://sandbox.zarinpal.com/pg/v4")
    url = f"{base.rstrip('/')}/{path.lstrip('/')}"
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ZarinpalError("ارتباط با درگاه پرداخت برقرار نشد.") from exc

    errors = data.get("errors") or {}
    if errors:
        raise ZarinpalError(str(errors))
    return data.get("data") or {}


def request_payment(*, amount_toman, description, callback_url, mobile=""):
    merchant_id = getattr(settings, "ZARINPAL_MERCHANT_ID", "").strip()
    if not merchant_id:
        raise ZarinpalError("درگاه هنوز پیکربندی نشده است. Merchant ID زرین‌پال را در تنظیمات سایت وارد کنید.")

    data = _request("payment/request.json", {
        "merchant_id": merchant_id,
        "amount": int(amount_toman) * 10,
        "description": description[:500],
        "callback_url": callback_url,
        "metadata": {"mobile": mobile} if mobile else {},
    })
    code = data.get("code")
    authority = data.get("authority")
    if code not in (100, 101) or not authority:
        raise ZarinpalError(f"خطای ایجاد تراکنش زرین‌پال: {code}")
    return authority


def verify_payment(*, authority, amount_toman):
    merchant_id = getattr(settings, "ZARINPAL_MERCHANT_ID", "").strip()
    if not merchant_id:
        raise ZarinpalError("درگاه هنوز پیکربندی نشده است.")

    data = _request("payment/verify.json", {
        "merchant_id": merchant_id,
        "amount": int(amount_toman) * 10,
        "authority": authority,
    })
    code = data.get("code")
    if code not in (100, 101):
        raise ZarinpalError(f"پرداخت تأیید نشد: {code}")
    return {
        "ref_id": str(data.get("ref_id", "")),
        "code": code,
    }


def payment_url(authority):
    base = getattr(settings, "ZARINPAL_STARTPAY_BASE", "https://sandbox.zarinpal.com/pg/StartPay")
    return f"{base.rstrip('/')}/{authority}"
