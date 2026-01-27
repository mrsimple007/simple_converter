import logging
from datetime import datetime, timezone, timedelta
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

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db, admin_ids):
    """Handle /stats command - Show detailed statistics"""
    if str(update.effective_user.id) not in admin_ids:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    try:
        # Total users
        total_users_result = db.supabase.table('converter_users').select(
            'user_id', count='exact'
        ).execute()
        total_users = total_users_result.count or 0
        
        # Premium users
        premium_users_result = db.supabase.table('converter_users').select(
            'user_id', count='exact'
        ).eq('subscription_tier', 'premium').execute()
        premium_users = premium_users_result.count or 0
        
        # Active today
        today = datetime.now(timezone.utc).date().isoformat()
        active_today_result = db.supabase.table('converter_user_stats').select(
            'user_id', count='exact'
        ).eq('last_conversion_date', today).execute()
        active_today = active_today_result.count or 0
        
        # Active this week
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
        active_week_result = db.supabase.table('converter_user_stats').select(
            'user_id', count='exact'
        ).gte('last_conversion_date', week_ago).execute()
        active_week = active_week_result.count or 0
        
        # Total conversions
        total_conversions_result = db.supabase.table('file_conversions').select(
            'id', count='exact'
        ).execute()
        total_conversions = total_conversions_result.count or 0
        
        # Successful conversions
        success_conversions_result = db.supabase.table('file_conversions').select(
            'id', count='exact'
        ).eq('conversion_status', 'success').execute()
        success_conversions = success_conversions_result.count or 0
        
        # Failed conversions
        failed_conversions = total_conversions - success_conversions
        
        # Success rate
        success_rate = (success_conversions / total_conversions * 100) if total_conversions > 0 else 0
        
        # Conversions today
        today_conversions_result = db.supabase.table('file_conversions').select(
            'id', count='exact'
        ).gte('created_at', today).execute()
        today_conversions = today_conversions_result.count or 0
        
        # Pending payments
        pending_payments_result = db.supabase.table('converter_payments').select(
            'id', count='exact'
        ).eq('status', 'pending').execute()
        pending_payments = pending_payments_result.count or 0
        
        # Total revenue (approved payments only)
        revenue_result = db.supabase.table('converter_payments').select(
            'amount'
        ).eq('status', 'approved').execute()
        
        total_revenue = sum(payment['amount'] for payment in revenue_result.data) if revenue_result.data else 0
        
        # Most popular format conversions
        popular_formats_result = db.supabase.table('file_conversions').select(
            'original_format, target_format'
        ).limit(1000).execute()
        
        format_counts = {}
        if popular_formats_result.data:
            for conv in popular_formats_result.data:
                key = f"{conv['original_format']} → {conv['target_format']}"
                format_counts[key] = format_counts.get(key, 0) + 1
        
        top_formats = sorted(format_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        text = (
            "📊 <b>Bot Statistics</b>\n\n"
            "👥 <b>Users:</b>\n"
            f"• Total: <b>{total_users}</b>\n"
            f"• Premium: <b>{premium_users}</b> ({premium_users/total_users*100:.1f}% if total_users > 0 else 0%)\n"
            f"• Free: <b>{total_users - premium_users}</b>\n"
            f"• Active today: <b>{active_today}</b>\n"
            f"• Active this week: <b>{active_week}</b>\n\n"
            "📁 <b>Conversions:</b>\n"
            f"• Total: <b>{total_conversions}</b>\n"
            f"• Successful: <b>{success_conversions}</b> ({success_rate:.1f}%)\n"
            f"• Failed: <b>{failed_conversions}</b>\n"
            f"• Today: <b>{today_conversions}</b>\n"
            f"• Avg per user: <b>{total_conversions/total_users:.1f}</b>\n\n" if total_users > 0 else ""
            "💰 <b>Revenue:</b>\n"
            f"• Total: <b>{int(total_revenue):,} UZS</b>\n"
            f"• Pending payments: <b>{pending_payments}</b>\n\n"
        )
        
        if top_formats:
            text += "🔥 <b>Popular Conversions:</b>\n"
            for fmt, count in top_formats:
                text += f"• {fmt}: <b>{count}</b>x\n"
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Refresh", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("💰 Payments", callback_data="admin_payments"),
                InlineKeyboardButton("📝 Conversions", callback_data="admin_conversions")
            ],
            [
                InlineKeyboardButton("« Back", callback_data="admin_back")
            ]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db, admin_ids):
    """Handle /users command - User management"""
    if str(update.effective_user.id) not in admin_ids:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    try:
        # Get recent users
        users_result = db.supabase.table('converter_users').select(
            'user_id, username, first_name, subscription_tier, created_at'
        ).order('created_at', desc=True).limit(10).execute()
        
        text = "👥 <b>Recent Users (Last 10)</b>\n\n"
        
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
                InlineKeyboardButton("🔍 Search User", callback_data="admin_search_user"),
                InlineKeyboardButton("💎 Premium Users", callback_data="admin_premium_users")
            ],
            [
                InlineKeyboardButton("« Back", callback_data="admin_back")
            ]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in users command: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def admin_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, db):
    """Handle admin stats button refresh"""
    query = update.callback_query
    await query.answer("Refreshing stats...")
    
    # Reuse stats command logic but for callback
    try:
        # Total users
        total_users_result = db.supabase.table('converter_users').select(
            'user_id', count='exact'
        ).execute()
        total_users = total_users_result.count or 0
        
        # Premium users
        premium_users_result = db.supabase.table('converter_users').select(
            'user_id', count='exact'
        ).eq('subscription_tier', 'premium').execute()
        premium_users = premium_users_result.count or 0
        
        # Active today
        today = datetime.now(timezone.utc).date().isoformat()
        active_today_result = db.supabase.table('converter_user_stats').select(
            'user_id', count='exact'
        ).eq('last_conversion_date', today).execute()
        active_today = active_today_result.count or 0
        
        # Total conversions
        total_conversions_result = db.supabase.table('file_conversions').select(
            'id', count='exact'
        ).execute()
        total_conversions = total_conversions_result.count or 0
        
        # Success rate
        success_conversions_result = db.supabase.table('file_conversions').select(
            'id', count='exact'
        ).eq('conversion_status', 'success').execute()
        success_conversions = success_conversions_result.count or 0
        
        success_rate = (success_conversions / total_conversions * 100) if total_conversions > 0 else 0
        
        text = (
            "📊 <b>Bot Statistics</b>\n\n"
            "👥 <b>Users:</b>\n"
            f"• Total: <b>{total_users}</b>\n"
            f"• Premium: <b>{premium_users}</b>\n"
            f"• Active today: <b>{active_today}</b>\n\n"
            "📁 <b>Conversions:</b>\n"
            f"• Total: <b>{total_conversions}</b>\n"
            f"• Success rate: <b>{success_rate:.1f}%</b>\n"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Refresh", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("💰 Payments", callback_data="admin_payments"),
                InlineKeyboardButton("📝 Conversions", callback_data="admin_conversions")
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
        logger.error(f"Error refreshing stats: {e}")
        await query.answer(f"❌ Error: {e}", show_alert=True)


async def admin_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, db):
    """Handle back to admin dashboard"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Get admin statistics
        total_users_result = db.supabase.table('converter_users').select(
            'user_id', count='exact'
        ).execute()
        total_users = total_users_result.count or 0
        
        today = datetime.now(timezone.utc).date().isoformat()
        active_today_result = db.supabase.table('converter_user_stats').select(
            'user_id', count='exact'
        ).eq('last_conversion_date', today).execute()
        todays_active_users = active_today_result.count or 0
        
        total_files_result = db.supabase.table('file_conversions').select(
            'id', count='exact'
        ).execute()
        total_processed_files = total_files_result.count or 0
        
        successful_files_result = db.supabase.table('file_conversions').select(
            'id', count='exact'
        ).eq('conversion_status', 'success').execute()
        successful_files = successful_files_result.count or 0
        
        success_rate = (successful_files / total_processed_files * 100) if total_processed_files > 0 else 0
        avg_files_per_user = total_processed_files / total_users if total_users > 0 else 0
        
        admin_message = (
            "👑 <b>Admin Dashboard</b>\n\n"
            f"📊 Total Users: <b>{total_users}</b>\n"
            f"👥 Active Users Today: <b>{todays_active_users}</b>\n"
            f"📝 Total Processed Files: <b>{total_processed_files}</b>\n\n"
            "📈 <b>Statistics:</b>\n"
            f"• Average files per user: <b>{avg_files_per_user:.1f}</b>\n"
            f"• Success rate: <b>{success_rate:.1f}%</b>\n"
            f"• Successful conversions: <b>{successful_files}</b>\n\n"
            "🔧 <b>Admin Commands:</b>\n"
            "/stats - Detailed statistics\n"
            "/users - User management\n"
            "/broadcast - Send message to all users"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("💰 Payments", callback_data="admin_payments"),
                InlineKeyboardButton("📝 Conversions", callback_data="admin_conversions")
            ],
            [
                InlineKeyboardButton("🔄 Use Bot", callback_data="use_bot")
            ]
        ]
        
        await query.edit_message_text(
            admin_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error going back to admin dashboard: {e}")
        await query.answer(f"❌ Error: {e}", show_alert=True)