"""
Additional admin callback handlers
"""

import logging
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


async def admin_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, db):
    """Handle admin users button"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Get recent users
        users_result = db.supabase.table('converter_users').select(
            'user_id, username, first_name, subscription_tier, created_at'
        ).order('created_at', desc=True).limit(15).execute()
        
        text = "👥 <b>Recent Users (Last 15)</b>\n\n"
        
        if users_result.data:
            for user in users_result.data:
                user_id = user['user_id']
                username = f"@{user['username']}" if user.get('username') else user.get('first_name', 'Unknown')
                tier = "💎" if user.get('subscription_tier') == 'premium' else "🆓"
                created = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
                
                text += f"{tier} {username} (<code>{user_id}</code>)\n   Joined: {created}\n\n"
        else:
            text += "No users found."
        
        keyboard = [
            [
                InlineKeyboardButton("💎 Premium Users", callback_data="admin_premium_users"),
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton("« Back", callback_data="admin_back")
            ]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in admin users callback: {e}")
        await query.answer(f"❌ Error: {e}", show_alert=True)


async def admin_payments_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, db):
    """Handle admin payments button"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Get recent payments
        payments_result = db.supabase.table('converter_payments').select(
            'id, user_id, amount, status, created_at'
        ).order('created_at', desc=True).limit(10).execute()
        
        # Get pending count
        pending_result = db.supabase.table('converter_payments').select(
            'id', count='exact'
        ).eq('status', 'pending').execute()
        pending_count = pending_result.count or 0
        
        # Get total revenue
        revenue_result = db.supabase.table('converter_payments').select(
            'amount'
        ).eq('status', 'approved').execute()
        total_revenue = sum(p['amount'] for p in revenue_result.data) if revenue_result.data else 0
        
        text = (
            "💰 <b>Payment Management</b>\n\n"
            f"⏳ Pending: <b>{pending_count}</b>\n"
            f"💵 Total Revenue: <b>{int(total_revenue):,} UZS</b>\n\n"
            "<b>Recent Payments:</b>\n\n"
        )
        
        if payments_result.data:
            status_emoji = {
                'pending': '⏳',
                'approved': '✅',
                'rejected': '❌'
            }
            
            for payment in payments_result.data:
                status = status_emoji.get(payment['status'], '❓')
                created = datetime.fromisoformat(payment['created_at'].replace('Z', '+00:00')).strftime('%m-%d %H:%M')
                text += (
                    f"{status} <code>{payment['user_id']}</code> - "
                    f"{int(payment['amount']):,} UZS\n"
                    f"   {created}\n\n"
                )
        else:
            text += "No payments found."
        
        keyboard = [
            [
                InlineKeyboardButton("⏳ Pending", callback_data="admin_pending_payments"),
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton("« Back", callback_data="admin_back")
            ]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in admin payments callback: {e}")
        await query.answer(f"❌ Error: {e}", show_alert=True)


async def admin_conversions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, db):
    """Handle admin conversions button"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Get recent conversions
        conversions_result = db.supabase.table('file_conversions').select(
            'user_id, original_format, target_format, conversion_status, created_at'
        ).order('created_at', desc=True).limit(15).execute()
        
        # Get today's stats
        today = datetime.now(timezone.utc).date().isoformat()
        today_result = db.supabase.table('file_conversions').select(
            'id', count='exact'
        ).gte('created_at', today).execute()
        today_count = today_result.count or 0
        
        text = (
            "📝 <b>Recent Conversions</b>\n\n"
            f"Today: <b>{today_count}</b> conversions\n\n"
            "<b>Latest Activity:</b>\n\n"
        )
        
        if conversions_result.data:
            status_emoji = {
                'success': '✅',
                'failed': '❌',
                'processing': '⏳'
            }
            
            for conv in conversions_result.data:
                status = status_emoji.get(conv['conversion_status'], '❓')
                created = datetime.fromisoformat(conv['created_at'].replace('Z', '+00:00')).strftime('%m-%d %H:%M')
                text += (
                    f"{status} <code>{conv['user_id']}</code>: "
                    f"{conv['original_format']} → {conv['target_format']}\n"
                    f"   {created}\n\n"
                )
        else:
            text += "No conversions yet."
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("« Back", callback_data="admin_back")
            ]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in admin conversions callback: {e}")
        await query.answer(f"❌ Error: {e}", show_alert=True)


async def admin_premium_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, db):
    """Handle premium users list"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Get premium users
        premium_result = db.supabase.table('converter_users').select(
            'user_id, username, first_name, subscription_expires_at'
        ).eq('subscription_tier', 'premium').order('subscription_expires_at', desc=True).execute()
        
        text = "💎 <b>Premium Users</b>\n\n"
        
        if premium_result.data:
            for user in premium_result.data:
                username = f"@{user['username']}" if user.get('username') else user.get('first_name', 'Unknown')
                
                if user.get('subscription_expires_at'):
                    expiry = datetime.fromisoformat(user['subscription_expires_at'].replace('Z', '+00:00'))
                    days_left = (expiry - datetime.now(timezone.utc)).days
                    
                    if days_left > 0:
                        expiry_str = f"Expires in {days_left} days"
                    else:
                        expiry_str = "⚠️ Expired"
                else:
                    expiry_str = "N/A"
                
                text += f"💎 {username} (<code>{user['user_id']}</code>)\n   {expiry_str}\n\n"
        else:
            text += "No premium users yet."
        
        keyboard = [
            [
                InlineKeyboardButton("👥 All Users", callback_data="admin_users"),
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton("« Back", callback_data="admin_back")
            ]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in premium users callback: {e}")
        await query.answer(f"❌ Error: {e}", show_alert=True)