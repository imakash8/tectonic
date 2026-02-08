"""
Payment service - handles Stripe payments for premium features
"""

import logging
import stripe
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    """Service for handling Stripe payments"""
    
    # Plan IDs (create these in Stripe dashboard or use test IDs)
    # Replace with your actual Stripe price IDs from https://dashboard.stripe.com/prices
    PLANS = {
        "premium_monthly": "price_test_monthly",  # Replace with your Stripe price ID
        "premium_yearly": "price_test_yearly"     # Replace with your Stripe price ID
    }
    
    @staticmethod
    def create_payment_intent(
        amount: int,
        currency: str = "usd",
        description: str = "",
        customer_email: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe payment intent
        
        Args:
            amount: Amount in cents (e.g., 5000 for $50.00)
            currency: Currency code (default: usd)
            description: Payment description
            customer_email: Customer email for receipt
        
        Returns:
            Payment intent object with client_secret
        """
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                description=description,
                receipt_email=customer_email,
                metadata={
                    "integration": "tectonic_trading_platform"
                }
            )
            
            logger.info(f"Created payment intent: {intent.id} for ${amount/100}")
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency
            }
            
        except stripe.error.CardError as e:
            logger.error(f"Card error: {e.user_message}")
            return None
        except stripe.error.RateLimitError:
            logger.error("Stripe rate limit exceeded")
            return None
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Invalid request to Stripe: {e}")
            return None
        except stripe.error.APIConnectionError:
            logger.error("Network error connecting to Stripe")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating payment intent: {e}")
            return None
    
    @staticmethod
    def get_payment_intent(payment_intent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a payment intent"""
        
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
                "client_secret": intent.client_secret,
                "created": intent.created
            }
        except Exception as e:
            logger.error(f"Error retrieving payment intent: {e}")
            return None
    
    @staticmethod
    def create_customer(email: str, name: str = "") -> Optional[str]:
        """Create a Stripe customer"""
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                description=f"Tectonic Trading Platform user"
            )
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer.id
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None
    
    @staticmethod
    def create_subscription(
        customer_email: str,
        plan_id: str,
        payment_method_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe subscription
        
        Args:
            customer_email: Customer email
            plan_id: Stripe plan ID (monthly or yearly)
            payment_method_id: Stripe payment method ID
        
        Returns:
            Subscription object
        """
        
        try:
            # Create customer if doesn't exist
            customer = stripe.Customer.create(
                email=customer_email,
                payment_method=payment_method_id,
                invoice_settings={"default_payment_method": payment_method_id}
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": plan_id}],
                expand=["latest_invoice.payment_intent"]
            )
            
            logger.info(f"Created subscription {subscription.id} for {customer_email}")
            return {
                "subscription_id": subscription.id,
                "customer_id": customer.id,
                "status": subscription.status,
                "plan_id": plan_id,
                "current_period_end": subscription.current_period_end
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return None
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """Cancel a subscription"""
        
        try:
            stripe.Subscription.delete(subscription_id)
            logger.info(f"Cancelled subscription {subscription_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return False
    
    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        
        try:
            sub = stripe.Subscription.retrieve(subscription_id)
            return {
                "subscription_id": sub.id,
                "status": sub.status,
                "plan_id": sub.items.data[0].price.id if sub.items.data else None,
                "current_period_end": sub.current_period_end,
                "cancel_at": sub.cancel_at
            }
        except Exception as e:
            logger.error(f"Error retrieving subscription: {e}")
            return None

# Create singleton instance
payment_service = PaymentService()
