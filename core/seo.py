import json
from urllib.parse import urljoin

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.sitemaps import Sitemap


PUBLIC_URL_NAMES = (
    "home",
    "about",
    "contact",
    "privacy",
    "terms",
    "refund",
    "subscription-catalog",
)

NOINDEX_PREFIXES = (
    "/login/",
    "/register/",
    "/account/",
    "/otp/",
    "/dashboard/",
    "/teacher/",
    "/content/",
    "/student/",
    "/placement/",
    "/practice/",
    "/subscriptions/mine/",
    "/subscriptions/buy/",
    "/subscriptions/payment/",
    "/api/",
    "/admin/",
)


def seo_context(request):
    path = request.path or "/"
    canonical = urljoin(settings.SEO_SITE_URL + "/", path.lstrip("/"))

    if path == "/":
        description = (
            "پیچک دانش؛ سکوی هوشمند یادگیری پایه ششم برای تعیین سطح، "
            "تمرین، آزمون، تحلیل عملکرد و پیشرفت دانش‌آموزان."
        )
    elif path == "/about/":
        description = "آشنایی با پیچک دانش؛ مسیر منظم و قابل‌اندازه‌گیری یادگیری، تمرین و ارزیابی پایه ششم."
    elif path == "/contact/":
        description = "راه‌های ارتباط و پشتیبانی پیچک دانش برای حساب کاربری، آزمون‌ها، اشتراک و خرید."
    elif path == "/subscriptions/":
        description = "اشتراک‌ها و بسته‌های آموزشی پیچک دانش برای یادگیری هدفمند پایه ششم."
    else:
        description = "پیچک دانش؛ یادگیری، تمرین، آزمون و پیشرفت برای دانش‌آموزان پایه ششم."

    robots = "noindex, nofollow" if path.startswith(NOINDEX_PREFIXES) else "index, follow"

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": ["Organization", "EducationalOrganization"],
                "@id": f"{settings.SEO_SITE_URL}/#organization",
                "name": "پیچک دانش",
                "url": settings.SEO_SITE_URL,
                "description": "سکوی آموزشی و یادگیری برای دانش‌آموزان پایه ششم.",
            },
            {
                "@type": "WebSite",
                "@id": f"{settings.SEO_SITE_URL}/#website",
                "name": "پیچک دانش",
                "url": settings.SEO_SITE_URL,
                "inLanguage": "fa-IR",
                "publisher": {"@id": f"{settings.SEO_SITE_URL}/#organization"},
            },
        ],
    }

    return {
        "seo_canonical": canonical,
        "seo_description": description,
        "seo_robots": robots,
        "seo_schema": json.dumps(schema, ensure_ascii=False),
    }


class PublicSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return PUBLIC_URL_NAMES

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == "home" else 0.7


def robots_txt(request):
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /api/\n"
        "\n"
        f"Sitemap: {settings.SEO_SITE_URL}/sitemap.xml\n"
    )
    return HttpResponse(body, content_type="text/plain; charset=utf-8")
