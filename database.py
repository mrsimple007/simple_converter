"""
Database manager for Supabase operations
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
load_dotenv()


logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.environ.get("ACTIVITY_SUPABASE_URL"),
            os.environ.get("ACTIVITY_SUPABASE_KEY")
        )
    
    # User Management
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by user_id"""
        try:
            result = self.supabase.table('users').select('*').eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def create_user(self, user_id: int, username: str = None, 
                         first_name: str = None, last_name: str = None,
                         language_code: str = 'en') -> bool:
        """Create a new user"""
        try:
            data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'language_code': language_code,
                'is_subscribed': False
            }
            self.supabase.table('users').insert(data).execute()
            
            # Create user stats entry
            self.supabase.table('user_stats').insert({'user_id': user_id}).execute()
            return True
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return False
    
    async def update_user_language(self, user_id: int, language_code: str) -> bool:
        """Update user's language preference"""
        try:
            self.supabase.table('users').update(
                {'language_code': language_code}
            ).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating user language {user_id}: {e}")
            return False
    
    async def is_user_subscribed(self, user_id: int) -> bool:
        """Check if user has active subscription"""
        try:
            user = await self.get_user(user_id)
            if not user or not user.get('is_subscribed'):
                return False
            
            if user.get('subscription_expires_at'):
                expiry = datetime.fromisoformat(user['subscription_expires_at'].replace('Z', '+00:00'))
                return expiry > datetime.now(timezone.utc)
            
            return False
        except Exception as e:
            logger.error(f"Error checking subscription for {user_id}: {e}")
            return False
    
    async def activate_subscription(self, user_id: int, days: int) -> bool:
        """Activate or extend user subscription"""
        try:
            user = await self.get_user(user_id)
            current_expiry = None
            
            if user and user.get('subscription_expires_at'):
                current_expiry = datetime.fromisoformat(
                    user['subscription_expires_at'].replace('Z', '+00:00')
                )
            
            # If current subscription is active, extend from expiry date
            # Otherwise, start from now
            if current_expiry and current_expiry > datetime.now(timezone.utc):
                new_expiry = current_expiry + timedelta(days=days)
            else:
                new_expiry = datetime.now(timezone.utc) + timedelta(days=days)
            
            self.supabase.table('users').update({
                'is_subscribed': True,
                'subscription_expires_at': new_expiry.isoformat()
            }).eq('user_id', user_id).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error activating subscription for {user_id}: {e}")
            return False
    
    # Payment Management
    async def create_payment(self, user_id: int, plan_id: int, 
                            amount: float, file_id: str = None) -> Optional[int]:
        """Create a new payment record"""
        try:
            data = {
                'user_id': user_id,
                'plan_id': plan_id,
                'amount': amount,
                'payment_proof_file_id': file_id,
                'status': 'pending'
            }
            result = self.supabase.table('payments').insert(data).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            logger.error(f"Error creating payment for {user_id}: {e}")
            return None
    
    async def get_payment(self, payment_id: int) -> Optional[Dict[str, Any]]:
        """Get payment by ID"""
        try:
            result = self.supabase.table('payments').select('*').eq('id', payment_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting payment {payment_id}: {e}")
            return None
    
    async def approve_payment(self, payment_id: int, admin_id: int) -> bool:
        """Approve a payment"""
        try:
            payment = await self.get_payment(payment_id)
            if not payment:
                return False
            
            # Get plan details
            plan = self.supabase.table('subscription_plans').select('*').eq(
                'id', payment['plan_id']
            ).execute()
            
            if not plan.data:
                return False
            
            plan_data = plan.data[0]
            
            # Update payment status
            self.supabase.table('payments').update({
                'status': 'approved',
                'processed_at': datetime.now(timezone.utc).isoformat(),
                'processed_by': admin_id
            }).eq('id', payment_id).execute()
            
            # Activate subscription
            await self.activate_subscription(
                payment['user_id'],
                plan_data['duration_days']
            )
            
            return True
        except Exception as e:
            logger.error(f"Error approving payment {payment_id}: {e}")
            return False
    
    async def reject_payment(self, payment_id: int, admin_id: int, 
                            reason: str = None) -> bool:
        """Reject a payment"""
        try:
            self.supabase.table('payments').update({
                'status': 'rejected',
                'processed_at': datetime.now(timezone.utc).isoformat(),
                'processed_by': admin_id,
                'admin_notes': reason
            }).eq('id', payment_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error rejecting payment {payment_id}: {e}")
            return False
    
    # File Conversion Tracking
    async def log_conversion(self, user_id: int, original_filename: str,
                            original_format: str, target_format: str,
                            file_size: int, status: str = 'success',
                            error_message: str = None,
                            processing_time: float = None) -> bool:
        """Log a file conversion"""
        try:
            data = {
                'user_id': user_id,
                'original_filename': original_filename,
                'original_format': original_format,
                'target_format': target_format,
                'file_size_bytes': file_size,
                'conversion_status': status,
                'error_message': error_message,
                'processing_time_seconds': processing_time
            }
            self.supabase.table('file_conversions').insert(data).execute()
            
            # Update user stats if successful
            if status == 'success':
                await self.increment_user_stats(user_id, file_size)
            
            return True
        except Exception as e:
            logger.error(f"Error logging conversion for {user_id}: {e}")
            return False
    
    async def increment_user_stats(self, user_id: int, file_size: int) -> bool:
        """Increment user conversion statistics"""
        try:
            # Get current stats
            stats = self.supabase.table('user_stats').select('*').eq(
                'user_id', user_id
            ).execute()
            
            if not stats.data:
                return False
            
            current_stats = stats.data[0]
            today = datetime.now(timezone.utc).date()
            
            # Reset daily count if it's a new day
            conversions_today = current_stats.get('conversions_today', 0)
            last_date = current_stats.get('last_conversion_date')
            
            if last_date:
                last_date = datetime.fromisoformat(str(last_date)).date()
                if last_date < today:
                    conversions_today = 0
            
            # Update stats
            self.supabase.table('user_stats').update({
                'total_conversions': current_stats.get('total_conversions', 0) + 1,
                'conversions_today': conversions_today + 1,
                'last_conversion_date': today.isoformat(),
                'total_files_size_bytes': current_stats.get('total_files_size_bytes', 0) + file_size
            }).eq('user_id', user_id).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error incrementing stats for {user_id}: {e}")
            return False
    
    async def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user statistics"""
        try:
            result = self.supabase.table('user_stats').select('*').eq(
                'user_id', user_id
            ).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting stats for {user_id}: {e}")
            return None
    
    async def check_daily_limit(self, user_id: int, max_conversions: int) -> bool:
        """Check if user has reached daily conversion limit"""
        try:
            stats = await self.get_user_stats(user_id)
            if not stats:
                return False
            
            today = datetime.now(timezone.utc).date()
            last_date = stats.get('last_conversion_date')
            
            if last_date:
                last_date = datetime.fromisoformat(str(last_date)).date()
                if last_date < today:
                    return False  # New day, limit not reached
            
            conversions_today = stats.get('conversions_today', 0)
            
            # -1 means unlimited
            if max_conversions == -1:
                return False
            
            return conversions_today >= max_conversions
        except Exception as e:
            logger.error(f"Error checking daily limit for {user_id}: {e}")
            return False
    
    # Subscription Plans
    async def get_subscription_plans(self) -> list:
        """Get all active subscription plans"""
        try:
            result = self.supabase.table('subscription_plans').select('*').eq(
                'is_active', True
            ).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting subscription plans: {e}")
            return []
    
    async def get_plan_by_id(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Get subscription plan by ID"""
        try:
            result = self.supabase.table('subscription_plans').select('*').eq(
                'id', plan_id
            ).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting plan {plan_id}: {e}")
            return None