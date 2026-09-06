from dataclasses import dataclass
from uuid import uuid4


class PaymentGatewayError(Exception):
    """Base error raised by payment gateway adapters."""


@dataclass(frozen=True)
class PaymentRequest:
    reference: str
    payment_url: str


class TestGateway:
    """Local sandbox gateway used until a production provider is selected."""

    name = "test"

    @classmethod
    def create_payment(cls, *, purchase_id, amount_toman, description, callback_url):
        reference = f"TEST-{uuid4().hex[:20].upper()}"
        payment_url = f"/subscriptions/payment/test/?purchase={purchase_id}&ref={reference}"
        return PaymentRequest(reference=reference, payment_url=payment_url)

    @classmethod
    def verify_payment(cls, *, reference, amount_toman):
        if not reference.startswith("TEST-"):
            raise PaymentGatewayError("شناسه تراکنش آزمایشی معتبر نیست.")
        return {"reference": reference}


def get_gateway():
    # Intentionally isolated behind one function so a real provider can be
    # plugged in later without changing the purchase/subscription domain logic.
    return TestGateway
