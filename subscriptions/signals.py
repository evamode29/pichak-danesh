from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Purchase, Subscription


@receiver(post_save, sender=Purchase)
def activate_subscription_for_purchase(sender, instance, **kwargs):
    if instance.status not in {Purchase.Status.PAID, Purchase.Status.GIFT}:
        return
    plan = getattr(instance.product, "subscription_plan", None)
    if not plan or hasattr(instance, "subscription"):
        return

    now = timezone.now()
    current = Subscription.active_for(instance.user)
    starts_at = current.ends_at if current else now
    ends_at = starts_at + timezone.timedelta(days=plan.duration_days)
    Subscription.objects.create(
        user=instance.user,
        plan=plan,
        starts_at=starts_at,
        ends_at=ends_at,
        source=Subscription.Source.PURCHASE if instance.status == Purchase.Status.PAID else Subscription.Source.ADMIN,
        purchase=instance,
    )
