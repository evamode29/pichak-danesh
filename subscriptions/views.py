from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import ActivationCode, Content, Purchase, Product, Subscription, SubscriptionPlan


def _active_subscription(user):
    return Subscription.active_for(user) if user.is_authenticated else None


def catalog(request):
    products = Product.objects.filter(is_active=True).prefetch_related("contents")
    plans = SubscriptionPlan.objects.filter(is_active=True).select_related("product")
    return render(request, "subscriptions/catalog.html", {
        "products": products,
        "plans": plans,
        "active_subscription": _active_subscription(request.user),
    })


@login_required(login_url="login")
def my_subscription(request):
    active_subscription = _active_subscription(request.user)
    subscriptions = list(Subscription.objects.filter(user=request.user).select_related("plan").order_by("-ends_at"))
    purchases = list(Purchase.objects.filter(user=request.user).select_related("product").order_by("-created_at")[:20])

    if request.method == "POST":
        code = request.POST.get("code", "").strip().upper()
        if not code:
            messages.error(request, "کد فعال‌سازی را وارد کنید.")
            return redirect("my-subscription")

        with transaction.atomic():
            activation = ActivationCode.objects.select_for_update().select_related("plan").filter(code=code).first()
            if not activation or not activation.usable:
                messages.error(request, "این کد معتبر نیست یا ظرفیت استفاده از آن تمام شده است.")
                return redirect("my-subscription")

            now = timezone.now()
            current = Subscription.active_for(request.user)
            start = current.ends_at if current else now
            ends_at = start + timezone.timedelta(days=activation.days)
            Subscription.objects.create(user=request.user, plan=activation.plan, starts_at=start, ends_at=ends_at, source=Subscription.Source.ACTIVATION)
            activation.used_count += 1
            activation.save(update_fields=["used_count"])

        messages.success(request, f"اشتراک «{activation.plan.name}» با موفقیت فعال شد.")
        return redirect("my-subscription")

    return render(request, "subscriptions/my_subscription.html", {
        "active_subscription": active_subscription,
        "subscriptions": subscriptions,
        "purchases": purchases,
    })


@login_required(login_url="login")
def content_detail(request, slug):
    content = get_object_or_404(Content.objects.select_related("product"), slug=slug, is_published=True)
    return render(request, "subscriptions/content_detail.html", {
        "content": content,
        "has_access": content.has_access(request.user),
        "active_subscription": _active_subscription(request.user),
    })


@login_required(login_url="login")
def request_purchase(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if request.method != "POST":
        return redirect("subscription-catalog")
    if product.is_free or product.price == 0:
        Purchase.objects.create(user=request.user, product=product, amount=0, status=Purchase.Status.GIFT, reference="free")
        messages.success(request, "این محصول برای حساب شما فعال شد.")
    else:
        Purchase.objects.create(user=request.user, product=product, amount=product.price, status=Purchase.Status.PENDING)
        messages.info(request, "درخواست خرید ثبت شد. اتصال درگاه پرداخت را در مرحله بعد فعال می‌کنیم.")
    return redirect("my-subscription")
