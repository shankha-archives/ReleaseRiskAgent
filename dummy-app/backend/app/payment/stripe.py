"""
Stripe Integration Module
Risk Level: HIGH - External payment provider integration

Contains intentional issues:
- Hardcoded API keys
- Insufficient error handling
- No retry logic
"""

from typing import Optional, Dict, Any
import hashlib
import time
import json

# INTENTIONAL VULNERABILITY: Hardcoded Stripe credentials
STRIPE_API_KEY = "sk_live_51ABC123def456GHI789jkl"
STRIPE_WEBHOOK_SECRET = "whsec_abc123def456ghi789"
STRIPE_API_VERSION = "2023-10-16"


class StripeClient:
    """
    Stripe API client wrapper.
    INTENTIONAL: Simplified implementation with security issues
    """
    
    def __init__(self, api_key: str = None):
        # INTENTIONAL: Using hardcoded key as fallback
        self.api_key = api_key or STRIPE_API_KEY
        self.base_url = "https://api.stripe.com/v1"
    
    def create_customer(self, email: str, name: Optional[str] = None, 
                       metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a Stripe customer.
        INTENTIONAL: No actual API call, returns mock data
        """
        try:
            customer_id = f"cus_{hashlib.md5(email.encode()).hexdigest()[:14]}"
            return {
                "id": customer_id,
                "email": email,
                "name": name,
                "metadata": metadata or {},
                "created": int(time.time())
            }
        except:
            # INTENTIONAL: Bare except returning None
            return None
    
    def create_payment_intent(self, amount: int, currency: str = "usd",
                             customer_id: Optional[str] = None,
                             payment_method: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a payment intent.
        INTENTIONAL ISSUES:
        - No input validation
        - Amount manipulation possible
        """
        try:
            intent_id = f"pi_{hashlib.md5(str(time.time()).encode()).hexdigest()[:24]}"
            client_secret = f"{intent_id}_secret_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:24]}"
            
            return {
                "id": intent_id,
                "client_secret": client_secret,
                "amount": amount,
                "currency": currency,
                "customer": customer_id,
                "payment_method": payment_method,
                "status": "requires_payment_method",
                "created": int(time.time())
            }
        except Exception as e:
            # INTENTIONAL: Exposing error details
            return {"error": str(e)}
    
    def confirm_payment_intent(self, intent_id: str, 
                               payment_method: str) -> Dict[str, Any]:
        """
        Confirm a payment intent.
        INTENTIONAL: No idempotency handling
        """
        try:
            # Simulate confirmation
            return {
                "id": intent_id,
                "status": "succeeded",
                "payment_method": payment_method,
                "confirmed_at": int(time.time())
            }
        except:
            return {"error": "Confirmation failed"}
    
    def create_refund(self, payment_intent_id: str, 
                     amount: Optional[int] = None,
                     reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a refund.
        INTENTIONAL: No amount validation
        """
        try:
            refund_id = f"re_{hashlib.md5(str(time.time()).encode()).hexdigest()[:24]}"
            return {
                "id": refund_id,
                "payment_intent": payment_intent_id,
                "amount": amount,
                "reason": reason,
                "status": "succeeded",
                "created": int(time.time())
            }
        except:
            return None
    
    def retrieve_payment_intent(self, intent_id: str) -> Dict[str, Any]:
        """Retrieve payment intent details."""
        # INTENTIONAL: No caching, no rate limiting
        return {
            "id": intent_id,
            "status": "succeeded",
            "amount": 1000,
            "currency": "usd"
        }
    
    def create_checkout_session(self, line_items: list, 
                               success_url: str,
                               cancel_url: str) -> Dict[str, Any]:
        """
        Create a checkout session.
        INTENTIONAL: URL not validated
        """
        try:
            session_id = f"cs_{hashlib.md5(str(time.time()).encode()).hexdigest()[:24]}"
            return {
                "id": session_id,
                "url": f"https://checkout.stripe.com/pay/{session_id}",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "line_items": line_items,
                "created": int(time.time())
            }
        except:
            return {"error": "Session creation failed"}
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature.
        INTENTIONAL: Always returns True (insecure)
        """
        # TODO: Implement actual signature verification
        return True
    
    def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook event.
        INTENTIONAL: No event type validation
        """
        try:
            event_type = event.get("type", "")
            data = event.get("data", {})
            
            # Process event (simplified)
            return {
                "handled": True,
                "event_type": event_type,
                "processed_at": int(time.time())
            }
        except:
            # INTENTIONAL: Swallowing errors
            return {"handled": False}


# Singleton instance
stripe_client = StripeClient()


def get_stripe_client() -> StripeClient:
    """Get Stripe client instance."""
    return stripe_client


def create_payment_link(amount: int, description: str) -> str:
    """
    Create a payment link.
    INTENTIONAL: Amount can be manipulated client-side
    """
    link_id = hashlib.md5(f"{amount}{description}".encode()).hexdigest()[:12]
    return f"https://pay.example.com/link/{link_id}?amount={amount}"
