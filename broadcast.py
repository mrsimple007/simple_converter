"""
Broadcast system with multi-language support - ASYNC
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class BroadcastManager:
    """Manages broadcast messages to users"""
    
    def __init__(self, db):
        self.db = db
        self.active_broadcasts = {}
    
    async def start_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_ids):
        """Handle /broadcast command"""
        if str(update.effective_user.id) not in admin_ids:
            await update.message.reply_text("⛔ Unauthorized")
            return
        
        text = (
            "📢 <b>Broadcast Message</b>\n\n"
            "Select language for your broadcast message:\n\n"
            "⚠️ Message will be sent to all users in selected language(s)"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🇺🇿 Uzbek", callback_data="broadcast_lang_uz"),
                InlineKeyboardButton("🇷🇺 Russian", callback_data="broadcast_lang_ru"),
            ],
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="broadcast_lang_en"),
                InlineKeyboardButton("🌍 All Languages", callback_data="broadcast_lang_all"),
            ],
            [
                InlineKeyboardButton("« Cancel", callback_data="broadcast_cancel")
            ]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast language selection"""
        query = update.callback_query
        await query.answer()
        
        lang_code = query.data.split('_')[2]
        context.user_data['broadcast_lang'] = lang_code
        
        lang_names = {
            'uz': '🇺🇿 Uzbek',
            'ru': '🇷🇺 Russian',
            'en': '🇬🇧 English',
            'all': '🌍 All Languages'
        }
        
        text = (
            f"📢 <b>Broadcast to {lang_names[lang_code]}</b>\n\n"
            "Now send your message:\n\n"
            "You can send:\n"
            "• Text message\n"
            "• Photo with caption\n"
            "• Video with caption\n"
            "• Document with caption\n\n"
            "⚠️ Use HTML formatting if needed:\n"
            "<b>bold</b>, <i>italic</i>, <code>code</code>"
        )
        
        keyboard = [[InlineKeyboardButton("« Cancel", callback_data="broadcast_cancel")]]
        
        context.user_data['awaiting_broadcast_message'] = True
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    async def handle_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the broadcast message from admin"""
        if not context.user_data.get('awaiting_broadcast_message'):
            return
        
        lang_code = context.user_data.get('broadcast_lang')
        if not lang_code:
            return
        
        # Store message details
        message = update.message
        context.user_data['broadcast_message'] = {
            'text': message.text or message.caption,
            'photo': message.photo[-1].file_id if message.photo else None,
            'video': message.video.file_id if message.video else None,
            'document': message.document.file_id if message.document else None,
        }
        
        # Get user count for this language
        if lang_code == 'all':
            users_result = self.db.supabase.table('converter_users').select(
                'user_id', count='exact'
            ).execute()
        else:
            users_result = self.db.supabase.table('converter_users').select(
                'user_id', count='exact'
            ).eq('language_code', lang_code).execute()
        
        user_count = users_result.count or 0
        
        lang_names = {
            'uz': '🇺🇿 Uzbek',
            'ru': '🇷🇺 Russian',
            'en': '🇬🇧 English',
            'all': '🌍 All Languages'
        }
        
        # Preview message
        preview_text = (
            f"📢 <b>Broadcast Preview</b>\n\n"
            f"Language: {lang_names[lang_code]}\n"
            f"Recipients: <b>{user_count}</b> users\n\n"
            f"<b>Your message:</b>\n"
            f"{'─' * 30}\n"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Send Now", callback_data="broadcast_confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
            ]
        ]
        
        # Send preview
        if message.photo:
            await message.reply_photo(
                photo=message.photo[-1].file_id,
                caption=preview_text + (message.caption or ""),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        elif message.video:
            await message.reply_video(
                video=message.video.file_id,
                caption=preview_text + (message.caption or ""),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        elif message.document:
            await message.reply_document(
                document=message.document.file_id,
                caption=preview_text + (message.caption or ""),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply_text(
                preview_text + (message.text or ""),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
    
    async def confirm_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm and execute broadcast"""
        query = update.callback_query
        await query.answer("Starting broadcast...")
        
        lang_code = context.user_data.get('broadcast_lang')
        message_data = context.user_data.get('broadcast_message')
        
        if not lang_code or not message_data:
            await query.answer("❌ Broadcast data not found", show_alert=True)
            return
        
        # Get users
        if lang_code == 'all':
            users_result = self.db.supabase.table('converter_users').select('user_id').execute()
        else:
            users_result = self.db.supabase.table('converter_users').select(
                'user_id'
            ).eq('language_code', lang_code).execute()
        
        if not users_result.data:
            await query.edit_message_text("❌ No users found")
            return
        
        users = users_result.data
        total_users = len(users)
        
        # Update message to show progress
        progress_message = await query.edit_message_text(
            f"📤 <b>Broadcasting...</b>\n\n"
            f"Progress: 0/{total_users}\n"
            f"Success: 0\n"
            f"Failed: 0",
            parse_mode=ParseMode.HTML
        )
        
        # Execute broadcast
        success_count = 0
        failed_count = 0
        
        # Process in batches to avoid rate limits
        batch_size = 30  # Telegram allows 30 messages per second
        
        for i in range(0, total_users, batch_size):
            batch = users[i:i + batch_size]
            
            # Send to batch concurrently
            tasks = []
            for user in batch:
                task = self.send_broadcast_message(
                    context.bot,
                    user['user_id'],
                    message_data
                )
                tasks.append(task)
            
            # Wait for batch to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count results
            for result in results:
                if result is True:
                    success_count += 1
                else:
                    failed_count += 1
            
            # Update progress every batch
            current = i + len(batch)
            try:
                await progress_message.edit_text(
                    f"📤 <b>Broadcasting...</b>\n\n"
                    f"Progress: {current}/{total_users}\n"
                    f"✅ Success: {success_count}\n"
                    f"❌ Failed: {failed_count}",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
            
            # Rate limit delay between batches
            if i + batch_size < total_users:
                await asyncio.sleep(1)
        
        # Final report
        await progress_message.edit_text(
            f"✅ <b>Broadcast Complete!</b>\n\n"
            f"Total: {total_users}\n"
            f"✅ Sent: {success_count}\n"
            f"❌ Failed: {failed_count}\n\n"
            f"Success rate: {success_count/total_users*100:.1f}%",
            parse_mode=ParseMode.HTML
        )
        
        # Clear context
        context.user_data.pop('awaiting_broadcast_message', None)
        context.user_data.pop('broadcast_lang', None)
        context.user_data.pop('broadcast_message', None)
        
        logger.info(f"Broadcast complete: {success_count} sent, {failed_count} failed")
    
    async def send_broadcast_message(self, bot, user_id: int, message_data: dict) -> bool:
        """Send broadcast message to a single user"""
        try:
            text = message_data.get('text', '')
            photo = message_data.get('photo')
            video = message_data.get('video')
            document = message_data.get('document')
            
            if photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text,
                    parse_mode=ParseMode.HTML
                )
            elif video:
                await bot.send_video(
                    chat_id=user_id,
                    video=video,
                    caption=text,
                    parse_mode=ParseMode.HTML
                )
            elif document:
                await bot.send_document(
                    chat_id=user_id,
                    document=document,
                    caption=text,
                    parse_mode=ParseMode.HTML
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode=ParseMode.HTML
                )
            
            return True
            
        except TelegramError as e:
            logger.warning(f"Failed to send broadcast to user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending broadcast to user {user_id}: {e}")
            return False
    
    async def cancel_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel broadcast"""
        query = update.callback_query
        await query.answer("Broadcast cancelled")
        
        # Clear context
        context.user_data.pop('awaiting_broadcast_message', None)
        context.user_data.pop('broadcast_lang', None)
        context.user_data.pop('broadcast_message', None)
        
        await query.edit_message_text(
            "❌ <b>Broadcast Cancelled</b>",
            parse_mode=ParseMode.HTML
        )