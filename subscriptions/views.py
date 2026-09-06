from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import ActivationCode, Content, Purchase, Subscription, SubscriptionPlan, Product
from .payment_gateway import PaymentGatewayError, get_gateway


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
            ends_at = start + timedelta(days=activation.days)
            Subscription.objects.create(
                user=request.user,
                plan=activation.plan,
                starts_at=start,
                ends_at=ends_at,
                source=Subscription.Source.ACTIVATION,
            )
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
        Purchase.objects.create(
            user=request.user,
            product=product,
            amount=0,
            status=Purchase.Status.GIFT,
            reference="free",
        )
        messages.success(request, "این محصول برای حساب شما فعال شد.")
        return redirect("my-subscription")

    purchase = Purchase.objects.create(
        user=request.user,
        product=product,
        amount=product.price,
        status=Purchase.Status.PENDING,
    )
    gateway = get_gateway()
    callback_url = request.build_absolute_uri(reverse("payment-callback"))

    try:
        payment = gateway.create_payment(
            purchase_id=purchase.id,
            amount_toman=purchase.amount,
            description=f"خرید {product.title} - پیچک دانش",
            callback_url=callback_url,
        )
    except PaymentGatewayError as exc:
        purchase.status = Purchase.Status.CANCELLED
        purchase.save(update_fields=["status"])
        messages.error(request, str(exc))
        return redirect("subscription-catalog")

    # `authority` is retained for backward migration compatibility and is now
    # treated as a provider-neutral gateway transaction reference.
    purchase.authority = payment.reference
    purchase.save(update_fields=["authority"])
    return redirect(payment.payment_url)


@login_required(login_url="login")
def test_payment(request):
    """Internal sandbox checkout. Replace this route with a real gateway later."""
    purchase_id = request.GET.get("purchase", "").strip()
    reference = request.GET.get("ref", "").strip()
    purchase = get_object_or_404(
        Purchase.objects.select_related("product"),
        pk=purchase_id,
        user=request.user,
        status=Purchase.Status.PENDING,
    )
    return render(request, "subscriptions/test_payment.html", {
        "purchase": purchase,
        "reference": reference,
    })


def payment_callback(request):
    """Provider-neutral callback endpoint; it must work without a login session."""
    reference = request.GET.get("ref", "").strip()
    purchase = Purchase.objects.filter(
        authority=reference,
        status=Purchase.Status.PENDING,
    ).select_related("product", "product__subscription_plan").first()

    if not purchase:
        return render(request, "subscriptions/payment_result.html", {
            "success": False,
            "title": "تراکنش پیدا نشد",
            "message": "این تراکنش معتبر نیست یا قبلاً پردازش شده است.",
        })

    gateway = get_gateway()
    try:
        result = gateway.verify_payment(reference=reference, amount_toman=purchase.amount)
    except PaymentGatewayError as exc:
        purchase.status = Purchase.Status.CANCELLED
        purchase.save(update_fields=["status"])
        return render(request, "subscriptions/payment_result.html", {
            "success": False,
            "title": "تأیید پرداخت ناموفق بود",
            "message": str(exc),
        })

    with transaction.atomic():
        purchase = Purchase.objects.select_for_update().select_related(
            "product", "product__subscription_plan"
        ).get(pk=purchase.pk)
        if purchase.status != Purchase.Status.PENDING:
            return render(request, "subscriptions/payment_result.html", {
                "success": purchase.status == Purchase.Status.PAID,
                "title": "تراکنش قبلاً پردازش شده است",
                "message": "وضعیت خرید شما قبلاً ثبت شده است.",
                "reference": purchase.reference,
            })

        purchase.status = Purchase.Status.PAID
        purchase.reference = result["reference"]
        purchase.paid_at = timezone.now()
        purchase.save(update_fields=["status", "reference", "paid_at"])

        plan = getattr(purchase.product, "subscription_plan", None)
        if plan:
            current = Subscription.active_for(purchase.user)
            if current:
                current.ends_at = max(current.ends_at, timezone.now()) + timedelta(days=plan.duration_days)
                current.save(update_fields=["ends_at"])
            else:
                now = timezone.now()
                Subscription.objects.create(
                    user=purchase.user,
                    plan=plan,
                    starts_at=now,
                    ends_at=now + timedelta(days=plan.duration_days),
                    source=Subscription.Source.PURCHASE,
                    purchase=purchase,
                )

    return render(request, "subscriptions/payment_result.html", {
        "success": True,
        "title": "پرداخت با موفقیت انجام شد 🎉",
        "message": "اشتراک شما فعال شد و حالا می‌توانید از محتوای ویژه پیچک دانش استفاده کنید.",
        "reference": purchase.reference,
    })


def test_payment_callback(request):
    """Sandbox payment action used by the local test checkout page."""
    if request.method != "POST":
        return redirect("subscription-catalog")
    return payment_callback(request)
