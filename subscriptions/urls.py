from django.urls import path

from .views import catalog, content_detail, my_subscription, request_purchase


urlpatterns = [
    path("", catalog, name="subscription-catalog"),
    path("mine/", my_subscription, name="my-subscription"),
    path("content/<slug:slug>/", content_detail, name="subscription-content"),
    path("buy/<int:product_id>/", request_purchase, name="subscription-buy"),
]
