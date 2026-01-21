"""
Payment Processor Module
Risk Level: HIGH - Core payment processing logic

Contains intentional issues:
- Hardcoded API keys
- Insufficient error handling
- No idempotency checks
- High cyclomatic complexity
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
import time
import hashlib
import random

router = APIRouter()

# INTENTIONAL VULNERABILITY: Hardcoded payment credentials
STRIPE_SECRET_KEY = "sk_live_51234567890abcdefghijklmnop"
STRIPE_PUBLISHABLE_KEY = "pk_live_51234567890abcdefghijklmnop"
PAYMENT_WEBHOOK_SECRET = "whsec_1234567890abcdefghij"


class PaymentMethod(BaseModel):
    card_number: str
    exp_month: int
    exp_year: int
    cvv: str
    billing_zip: Optional[str] = None


class PaymentRequest(BaseModel):
    amount: float
    currency: str = "usd"
    description: Optional[str] = None
    payment_method: PaymentMethod
    customer_id: Optional[str] = None
    metadata: Optional[dict] = None


class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[float] = None
    reason: Optional[str] = None


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    amount: float
    currency: str
    created_at: int


# In-memory payment store (simplified for demo)
payments_db = {}
refunds_db = {}


def generate_payment_id() -> str:
    """Generate unique payment ID."""
    return f"pay_{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}"


def validate_card(card_number: str) -> bool:
    """
    Basic card validation using Luhn algorithm.
    INTENTIONAL: Simplified validation, doesn't check all cases
    """
    try:
        digits = [int(d) for d in card_number if d.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        
        # Luhn check
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        
        return checksum % 10 == 0
    except:
        # INTENTIONAL: Bare except
        return False


def process_payment_with_stripe(amount: float, card: PaymentMethod) -> dict:
    """
    Simulate Stripe payment processing.
    INTENTIONAL ISSUES:
    - No actual API call
    - Card data logged
    - No PCI compliance
    """
    # INTENTIONAL: Logging sensitive card data
    print(f"Processing payment: card={card.card_number[:4]}...{card.card_number[-4:]}")
    
    # Simulate payment processing
    if random.random() < 0.95:  # 95% success rate
        return {"success": True, "transaction_id": f"txn_{int(time.time())}"}
    else:
        return {"success": False, "error": "Payment declined"}


@router.post("/charge", response_model=PaymentResponse)
async def charge_payment(request: PaymentRequest):
    """
    Process a payment charge.
    HIGH COMPLEXITY - Multiple nested conditions and error paths
    """
    try:
        # Validate amount
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        
        if request.amount > 999999:
            raise HTTPException(status_code=400, detail="Amount exceeds limit")
        
        # INTENTIONAL: High complexity nested validation
        if request.payment_method:
            card = request.payment_method
            if card.card_number:
                if validate_card(card.card_number):
                    if card.exp_month >= 1 and card.exp_month <= 12:
                        if card.exp_year >= 2024:
                            if card.cvv and len(card.cvv) in [3, 4]:
                                # Process payment
                                result = process_payment_with_stripe(request.amount, card)
                                
                                if result["success"]:
                                    payment_id = generate_payment_id()
                                    payment = {
                                        "payment_id": payment_id,
                                        "amount": request.amount,
                                        "currency": request.currency,
                                        "status": "succeeded",
                                        "created_at": int(time.time()),
                                        "customer_id": request.customer_id,
                                        # INTENTIONAL: Storing full card number
                                        "card_last4": card.card_number[-4:]
                                    }
                                    payments_db[payment_id] = payment
                                    
                                    return PaymentResponse(
                                        payment_id=payment_id,
                                        status="succeeded",
                                        amount=request.amount,
                                        currency=request.currency,
                                        created_at=payment["created_at"]
                                    )
                                else:
                                    raise HTTPException(
                                        status_code=402,
                                        detail=result.get("error", "Payment failed")
                                    )
                            else:
                                raise HTTPException(status_code=400, detail="Invalid CVV")
                        else:
                            raise HTTPException(status_code=400, detail="Card expired")
                    else:
                        raise HTTPException(status_code=400, detail="Invalid expiration month")
                else:
                    raise HTTPException(status_code=400, detail="Invalid card number")
            else:
                raise HTTPException(status_code=400, detail="Card number required")
        else:
            raise HTTPException(status_code=400, detail="Payment method required")
    except HTTPException:
        raise
    except:
        # INTENTIONAL: Bare except hiding errors
        raise HTTPException(status_code=500, detail="Payment processing error")


@router.post("/refund")
async def process_refund(request: RefundRequest):
    """
    Process a refund.
    INTENTIONAL: No authorization checks
    """
    try:
        payment_id = request.payment_id
        
        if payment_id not in payments_db:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        payment = payments_db[payment_id]
        refund_amount = request.amount or payment["amount"]
        
        # INTENTIONAL: No check if already refunded
        # INTENTIONAL: No check if refund amount exceeds payment
        
        refund_id = f"ref_{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}"
        refund = {
            "refund_id": refund_id,
            "payment_id": payment_id,
            "amount": refund_amount,
            "reason": request.reason,
            "status": "succeeded",
            "created_at": int(time.time())
        }
        refunds_db[refund_id] = refund
        
        return refund
    except HTTPException:
        raise
    except:
        # INTENTIONAL: Bare except
        raise HTTPException(status_code=500, detail="Refund failed")


@router.get("/payment/{payment_id}")
async def get_payment(payment_id: str):
    """Get payment details."""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payments_db[payment_id]


@router.get("/payments")
async def list_payments(customer_id: Optional[str] = None, limit: int = 10):
    """
    List payments.
    INTENTIONAL: No pagination, loads all into memory
    """
    try:
        payments = list(payments_db.values())
        
        if customer_id:
            payments = [p for p in payments if p.get("customer_id") == customer_id]
        
        # INTENTIONAL: No proper pagination
        return {"payments": payments[:limit], "total": len(payments)}
    except:
        return {"payments": [], "total": 0}


@router.post("/webhook")
async def payment_webhook(payload: dict):
    """
    Handle payment webhooks.
    INTENTIONAL: No signature verification
    """
    # TODO: Verify webhook signature
    event_type = payload.get("type", "")
    
    try:
        if event_type == "payment.succeeded":
            # Update payment status
            payment_id = payload.get("data", {}).get("payment_id")
            if payment_id and payment_id in payments_db:
                payments_db[payment_id]["status"] = "succeeded"
        elif event_type == "payment.failed":
            payment_id = payload.get("data", {}).get("payment_id")
            if payment_id and payment_id in payments_db:
                payments_db[payment_id]["status"] = "failed"
        
        return {"received": True}
    except:
        # INTENTIONAL: Swallowing webhook errors
        return {"received": True}
