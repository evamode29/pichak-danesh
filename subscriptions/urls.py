from django.urls import path

from .views import (
    catalog,
    content_detail,
    my_subscription,
    payment_callback,
    request_purchase,
    test_payment,
    test_payment_callback,
)


urlpatterns = [
    path("", catalog, name="subscription-catalog"),
    path("mine/", my_subscription, name="my-subscription"),
    path("content/<slug:slug>/", content_detail, name="subscription-content"),
    path("buy/<int:product_id>/", request_purchase, name="subscription-buy"),
    path("payment/test/", test_payment, name="test-payment"),
    path("payment/test/complete/", test_payment_callback, name="test-payment-complete"),
    path("payment/callback/", payment_callback, name="payment-callback"),
]
