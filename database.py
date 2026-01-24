"""
Database manager for Supabase operations - Fixed for correct table names
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
            result = self.supabase.table('converter_users').select('*').eq('user_id', user_id).execute()
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
                'user_id': user_id,  # Changed from 'id' to 'user_id'
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'language_code': language_code,
                'subscription_tier': 'free',  # Default to free tier
            }
            self.supabase.table('converter_users').insert(data).execute()
            
            # Create user stats entry
            self.supabase.table('converter_user_stats').insert({
                'user_id': user_id,
                'conversions_today': 0,
                'total_conversions': 0,
                'total_files_size_bytes': 0
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return False
    
    async def update_user_language(self, user_id: int, language_code: str) -> bool:
        """Update user's language preference"""
        try:
            self.supabase.table('converter_users').update(
                {'language_code': language_code}
            ).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating user language {user_id}: {e}")
            return False
    
    async def get_user_tier(self, user_id: int) -> str:
        """Get user's subscription tier (free/premium)"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return 'free'
            
            # Check if premium subscription is still valid
            if user.get('subscription_tier') == 'premium':
                if user.get('subscription_expires_at'):
                    expiry = datetime.fromisoformat(user['subscription_expires_at'].replace('Z', '+00:00'))
                    if expiry > datetime.now(timezone.utc):
                        return 'premium'
                    else:
                        # Subscription expired, downgrade to free
                        await self.downgrade_to_free(user_id)
                        return 'free'
            
            return user.get('subscription_tier', 'free')
        except Exception as e:
            logger.error(f"Error getting user tier {user_id}: {e}")
            return 'free'
    
    async def is_premium_user(self, user_id: int) -> bool:
        """Check if user has active premium subscription"""
        tier = await self.get_user_tier(user_id)
        return tier == 'premium'
    
    async def upgrade_to_premium(self, user_id: int, days: int) -> bool:
        """Upgrade user to premium tier"""
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
            
            self.supabase.table('converter_users').update({
                'subscription_tier': 'premium',
                'subscription_expires_at': new_expiry.isoformat()
            }).eq('user_id', user_id).execute()
            
            logger.info(f"✅ User {user_id} upgraded to premium until {new_expiry.isoformat()}")
            return True
        except Exception as e:
            logger.error(f"Error upgrading user {user_id} to premium: {e}")
            return False
    
    async def downgrade_to_free(self, user_id: int) -> bool:
        """Downgrade user to free tier"""
        try:
            self.supabase.table('converter_users').update({
                'subscription_tier': 'free',
                'subscription_expires_at': None
            }).eq('user_id', user_id).execute()
            
            logger.info(f"ℹ️ User {user_id} downgraded to free tier")
            return True
        except Exception as e:
            logger.error(f"Error downgrading user {user_id}: {e}")
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
            result = self.supabase.table('converter_payments').insert(data).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            logger.error(f"Error creating payment for {user_id}: {e}")
            return None
    
    async def get_payment(self, payment_id: int) -> Optional[Dict[str, Any]]:
        """Get payment by ID"""
        try:
            result = self.supabase.table('converter_payments').select('*').eq('id', payment_id).execute()
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
            self.supabase.table('converter_payments').update({
                'status': 'approved',
                'processed_at': datetime.now(timezone.utc).isoformat(),
                'processed_by': admin_id
            }).eq('id', payment_id).execute()
            
            # Upgrade to premium
            await self.upgrade_to_premium(
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
            self.supabase.table('converter_payments').update({
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
            stats = self.supabase.table('converter_user_stats').select('*').eq(
                'user_id', user_id
            ).execute()
            
            if not stats.data:
                # Create stats if not exists
                self.supabase.table('converter_user_stats').insert({
                    'user_id': user_id,
                    'conversions_today': 1,
                    'total_conversions': 1,
                    'last_conversion_date': datetime.now(timezone.utc).date().isoformat(),
                    'total_files_size_bytes': file_size
                }).execute()
                return True
            
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
            self.supabase.table('converter_user_stats').update({
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
            result = self.supabase.table('converter_user_stats').select('*').eq(
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