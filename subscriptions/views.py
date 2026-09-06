from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import ActivationCode, Content, Purchase, Product, Subscription, SubscriptionPlan
from .zarinpal import ZarinpalError, payment_url, request_payment, verify_payment


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
    product = get_object_or_404(Product.objects.select_related("subscription_plan"), pk=product_id, is_active=True)
    if request.method != "POST":
        return redirect("subscription-catalog")

    if product.is_free or product.price == 0:
        Purchase.objects.create(user=request.user, product=product, amount=0, status=Purchase.Status.GIFT, reference="free")
        messages.success(request, "این محصول برای حساب شما فعال شد.")
        return redirect("my-subscription")

    purchase = Purchase.objects.create(
        user=request.user,
        product=product,
        amount=product.price,
        status=Purchase.Status.PENDING,
    )
    callback_url = request.build_absolute_uri(reverse("zarinpal-callback"))

    try:
        authority = request_payment(
            amount_toman=purchase.amount,
            description=f"خرید {product.title} - پیچک دانش",
            callback_url=callback_url,
        )
    except ZarinpalError as exc:
        purchase.status = Purchase.Status.CANCELLED
        purchase.save(update_fields=["status"])
        messages.error(request, str(exc))
        return redirect("subscription-catalog")

    purchase.authority = authority
    purchase.save(update_fields=["authority"])
    return redirect(payment_url(authority))


@login_required(login_url="login")
def zarinpal_callback(request):
    authority = request.GET.get("Authority", "").strip()
    status = request.GET.get("Status", "").strip().upper()

    purchase = Purchase.objects.filter(
        user=request.user,
        authority=authority,
        status=Purchase.Status.PENDING,
    ).select_related("product", "product__subscription_plan").first()

    if not purchase:
        return render(request, "subscriptions/payment_result.html", {
            "success": False,
            "title": "تراکنش پیدا نشد",
            "message": "این تراکنش معتبر نیست یا قبلاً پردازش شده است.",
        })

    if status != "OK":
        purchase.status = Purchase.Status.CANCELLED
        purchase.save(update_fields=["status"])
        return render(request, "subscriptions/payment_result.html", {
            "success": False,
            "title": "پرداخت لغو شد",
            "message": "پرداخت انجام نشد. می‌توانید دوباره برای خرید اقدام کنید.",
        })

    try:
        result = verify_payment(authority=authority, amount_toman=purchase.amount)
    except ZarinpalError as exc:
        purchase.status = Purchase.Status.CANCELLED
        purchase.save(update_fields=["status"])
        return render(request, "subscriptions/payment_result.html", {
            "success": False,
            "title": "تأیید پرداخت ناموفق بود",
            "message": str(exc),
        })

    with transaction.atomic():
        purchase.status = Purchase.Status.PAID
        purchase.reference = result["ref_id"]
        purchase.paid_at = timezone.now()
        purchase.save(update_fields=["status", "reference", "paid_at"])

        plan = getattr(purchase.product, "subscription_plan", None)
        if plan:
            current = Subscription.active_for(purchase.user)
            if current:
                current.ends_at = max(current.ends_at, timezone.now()) + timezone.timedelta(days=plan.duration_days)
                current.save(update_fields=["ends_at"])
                Subscription.objects.filter(pk=current.pk).update(purchase=purchase, plan=plan, source=Subscription.Source.PURCHASE)
            else:
                now = timezone.now()
                Subscription.objects.create(
                    user=purchase.user,
                    plan=plan,
                    starts_at=now,
                    ends_at=now + timezone.timedelta(days=plan.duration_days),
                    source=Subscription.Source.PURCHASE,
                    purchase=purchase,
                )

    return render(request, "subscriptions/payment_result.html", {
        "success": True,
        "title": "پرداخت با موفقیت انجام شد 🎉",
        "message": "اشتراک شما فعال شد و حالا می‌توانید از محتوای ویژه پیچک دانش استفاده کنید.",
        "reference": purchase.reference,
    })
