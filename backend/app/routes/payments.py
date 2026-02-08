"""
Payment routes - handles Stripe integration for premium features
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.routes.auth import get_current_user
from app.services.payment_service import payment_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payments", tags=["payments"])

# Request/Response Models
class PaymentRequest(BaseModel):
    """Request to create a payment intent"""
    amount: int  # Amount in cents (e.g., 5000 for $50.00)
    description: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 5000,
                "description": "Premium subscription upgrade"
            }
        }

class SubscriptionRequest(BaseModel):
    """Request to create a subscription"""
    plan_id: str  # "premium_monthly" or "premium_yearly"
    payment_method_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "premium_monthly",
                "payment_method_id": "pm_test_visa"
            }
        }

class PaymentResponse(BaseModel):
    """Response from payment creation"""
    client_secret: str
    payment_intent_id: str
    status: str
    amount: int
    currency: str

class SubscriptionResponse(BaseModel):
    """Response from subscription creation"""
    subscription_id: str
    customer_id: str
    status: str
    plan_id: str

# Routes

@router.post("/create-payment-intent", response_model=PaymentResponse)
async def create_payment_intent(
    request: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Stripe payment intent for one-time payment
    
    - **amount**: Amount in cents (e.g., 5000 for $50.00)
    - **description**: Optional payment description
    
    Returns client_secret needed for frontend payment processing
    """
    
    try:
        if request.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )
        
        intent = payment_service.create_payment_intent(
            amount=request.amount,
            description=request.description or f"Tectonic Trading Platform payment",
            customer_email=current_user.email
        )
        
        if not intent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create payment intent. Please try again."
            )
        
        return PaymentResponse(**intent)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment intent for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating payment intent"
        )

@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Stripe subscription for premium features
    
    - **plan_id**: Either "premium_monthly" or "premium_yearly"
    - **payment_method_id**: Stripe payment method ID from frontend
    """
    
    try:
        if request.plan_id not in ["premium_monthly", "premium_yearly"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan_id. Must be 'premium_monthly' or 'premium_yearly'"
            )
        
        subscription = payment_service.create_subscription(
            customer_email=current_user.email,
            plan_id=request.plan_id,
            payment_method_id=request.payment_method_id
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create subscription. Please check your payment method."
            )
        
        return SubscriptionResponse(**subscription)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating subscription"
        )

@router.get("/payment-intent/{intent_id}")
async def get_payment_status(
    intent_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a payment intent
    
    Returns current status and details of the payment intent
    """
    
    try:
        intent = payment_service.get_payment_intent(intent_id)
        
        if not intent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment intent not found"
            )
        
        return intent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/subscription/{subscription_id}")
async def get_subscription_status(
    subscription_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a subscription
    
    Returns current subscription details and status
    """
    
    try:
        subscription = payment_service.get_subscription(subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        return subscription
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/subscription/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a subscription
    
    Returns success status
    """
    
    try:
        success = payment_service.cancel_subscription(subscription_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel subscription"
            )
        
        return {
            "status": "cancelled",
            "subscription_id": subscription_id,
            "message": "Subscription has been cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error cancelling subscription"
        )

# === Premium Tier Endpoints ===

@router.get("/plans")
async def get_premium_plans():
    """
    Get available premium plans
    
    Returns list of premium tiers with pricing
    """
    
    return {
        "plans": [
            {
                "id": "premium_monthly",
                "name": "Premium - Monthly",
                "price": 4900,  # $49.00
                "currency": "usd",
                "billing_cycle": "monthly",
                "features": [
                    "Unlimited trades",
                    "Real-time market data",
                    "Advanced analytics",
                    "AI trading signals",
                    "24/7 support",
                    "Portfolio tracking"
                ]
            },
            {
                "id": "premium_yearly",
                "name": "Premium - Yearly",
                "price": 49900,  # $499.00 (save $89)
                "currency": "usd",
                "billing_cycle": "yearly",
                "features": [
                    "Unlimited trades",
                    "Real-time market data",
                    "Advanced analytics",
                    "AI trading signals",
                    "Priority support",
                    "Portfolio tracking",
                    "Save $89 vs monthly"
                ]
            }
        ]
    }

@router.get("/subscription-status")
async def get_user_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's subscription status
    
    Returns premium tier, expiration date, and plan details
    """
    
    user = db.query(User).filter(User.id == current_user.id).first()
    
    return {
        "is_premium": user.is_premium,
        "subscription_tier": user.subscription_tier,
        "subscription_expires": user.subscription_expires,
        "stripe_subscription_id": user.stripe_subscription_id,
        "stripe_customer_id": user.stripe_customer_id
    }

@router.post("/upgrade-to-premium")
async def upgrade_to_premium(
    request: SubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upgrade user to premium subscription
    
    Creates Stripe subscription and updates user in database
    """
    
    try:
        # Create Stripe subscription
        subscription = payment_service.create_subscription(
            customer_email=current_user.email,
            plan_id=request.plan_id,
            payment_method_id=request.payment_method_id
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create subscription"
            )
        
        # Update user in database
        user = db.query(User).filter(User.id == current_user.id).first()
        user.is_premium = True
        user.stripe_subscription_id = subscription.get("subscription_id")
        user.stripe_customer_id = subscription.get("customer_id")
        user.subscription_tier = request.plan_id
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User {current_user.id} upgraded to {request.plan_id}")
        
        return {
            "status": "success",
            "message": f"Upgraded to {request.plan_id}",
            "subscription_id": subscription.get("subscription_id"),
            "is_premium": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error upgrading user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade to premium"
        )

@router.post("/cancel-premium")
async def cancel_premium_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel user's premium subscription
    
    Updates Stripe and user database
    """
    
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        
        if not user.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no active subscription"
            )
        
        # Cancel in Stripe
        success = payment_service.cancel_subscription(user.stripe_subscription_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel subscription in Stripe"
            )
        
        # Update user in database
        user.is_premium = False
        user.stripe_subscription_id = None
        user.subscription_tier = None
        user.subscription_expires = None
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User {current_user.id} cancelled premium subscription")
        
        return {
            "status": "success",
            "message": "Premium subscription cancelled",
            "is_premium": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling premium for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel premium subscription"
        )
