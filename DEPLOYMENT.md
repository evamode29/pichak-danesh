# استقرار پیچک دانش

## نصب

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

## اجرای Production

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## متغیرهای ضروری

نمونه کامل در `.env.example` قرار دارد. در سرور حتماً `DJANGO_SECRET_KEY` واقعی، `DJANGO_DEBUG=0`، دامنه در `DJANGO_ALLOWED_HOSTS` و آدرس‌های HTTPS در `DJANGO_CSRF_TRUSTED_ORIGINS` تنظیم شوند.

برای PostgreSQL متغیرهای `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` را تنظیم کنید.

برای پیامک، `SMS_API_URL`, `SMS_API_KEY` و در صورت نیاز `SMS_SENDER` را تنظیم کنید. Adapter فعلی یک درخواست JSON با Authorization Bearer ارسال می‌کند؛ هنگام انتخاب سرویس پیامک، payload آن سرویس را در `core/sms.py` مطابق مستندات همان ارائه‌دهنده تنظیم کنید.

## امنیت نهایی

بعد از فعال شدن HTTPS:

- `DJANGO_SECURE_SSL_REDIRECT=1`
- `DJANGO_SESSION_COOKIE_SECURE=1`
- `DJANGO_CSRF_COOKIE_SECURE=1`
- `DJANGO_HSTS_SECONDS=31536000`
- `DJANGO_HSTS_SUBDOMAINS=1`

سپس `python manage.py check --deploy` را اجرا کنید.
