import json
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse
from django.urls import reverse


class PublicSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return ("home",)

    def location(self, item):
        return reverse(item)


def seo_context(request):
    path = request.path or "/"
    canonical = urljoin(settings.SEO_SITE_URL + "/", path.lstrip("/"))
    description = (
        "پیچک دانش؛ فضای ساده پایه ششم برای ورود دانش‌آموزان، "
        "آزمون هوش تصویری و مشاهده نتیجه‌ها توسط معلم."
    )
    robots = "index, follow" if path == "/" else "noindex, nofollow"
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "پیچک دانش",
        "url": settings.SEO_SITE_URL,
        "inLanguage": "fa-IR",
        "description": description,
    }
    return {
        "seo_canonical": canonical,
        "seo_description": description,
        "seo_robots": robots,
        "seo_schema": json.dumps(schema, ensure_ascii=False),
    }


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
