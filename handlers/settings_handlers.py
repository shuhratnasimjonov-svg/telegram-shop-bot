"""
Settings handlers for the Telegram Shop Bot.
Handles user profile settings and preferences.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import UserStates
from keyboards import get_settings_keyboard, get_back_keyboard, get_language_keyboard
from database import db
from logger import logger

router = Router()


@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery, state: FSMContext):
    """Show settings menu."""
    try:
        user_id = callback.from_user.id
        await state.set_state(UserStates.in_settings)
        
        user = db.get_user(user_id)
        
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi.")
            return
        
        text = (
            "⚙️ Sozlamalar\n\n"
            f"👤 Ism: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}\n"
            f"📱 ID: {user_id}\n"
            f"📧 Username: @{user.get('username', 'N/A')}\n"
            f"📅 Qo'shilgan: {user.get('created_at', 'N/A')}\n\n"
            "Quyidagi sozlamalarni o'zgartiring:"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_settings_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in settings: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "change_language")
async def change_language(callback: CallbackQuery, state: FSMContext):
    """Change language."""
    try:
        text = "🌐 Tilni Tanlang:\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_language_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in change language: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    """Set language."""
    try:
        language = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        language_name = {
            "uz": "O'zbek",
            "ru": "Русский",
            "en": "English"
        }
        
        db.update_user_language(user_id, language)
        
        await callback.answer(f"✅ Til {language_name.get(language, 'O'zgartirildi')}ga o'zgartirildi!")
        
        text = "✅ Til muvaffaqiyatli o'zgartirildi."
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("settings")
        )
        
    except Exception as e:
        logger.error(f"Error in set language: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "notification_settings")
async def notification_settings(callback: CallbackQuery, state: FSMContext):
    """Notification settings."""
    try:
        user_id = callback.from_user.id
        user = db.get_user(user_id)
        
        notifications_enabled = user.get('notifications_enabled', True)
        email_notifications = user.get('email_notifications', True)
        
        text = (
            "🔔 Bildirishnomalar Sozlamalari\n\n"
            f"📱 Push bildirishnomalar: {'✅ Yoqilgan' if notifications_enabled else '❌ O'chirilgan'}\n"
            f"📧 Email bildirishnomalar: {'✅ Yoqilgan' if email_notifications else '❌ O'chirilgan'}\n\n"
            "Sozlamalarni o'zgartiring:"
        )
        
        from keyboards import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"📱 Push: {'🔔 O'chirish' if notifications_enabled else '🔔 Yoqish'}",
                    callback_data="toggle_push_notifications"
                )],
                [InlineKeyboardButton(
                    text=f"📧 Email: {'🔔 O'chirish' if email_notifications else '🔔 Yoqish'}",
                    callback_data="toggle_email_notifications"
                )],
                [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="settings")]
            ]
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in notification settings: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "toggle_push_notifications")
async def toggle_push_notifications(callback: CallbackQuery, state: FSMContext):
    """Toggle push notifications."""
    try:
        user_id = callback.from_user.id
        user = db.get_user(user_id)
        
        current_state = user.get('notifications_enabled', True)
        db.update_user_notifications(user_id, not current_state)
        
        await callback.answer(f"✅ Push bildirishnomalar {'🔔 O'chirildi' if current_state else '🔔 Yoqildi'}!")
        
        # Refresh the settings screen
        await notification_settings(callback, state)
        
    except Exception as e:
        logger.error(f"Error in toggle push notifications: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "toggle_email_notifications")
async def toggle_email_notifications(callback: CallbackQuery, state: FSMContext):
    """Toggle email notifications."""
    try:
        user_id = callback.from_user.id
        user = db.get_user(user_id)
        
        current_state = user.get('email_notifications', True)
        db.update_user_email_notifications(user_id, not current_state)
        
        await callback.answer(f"✅ Email bildirishnomalar {'🔔 O'chirildi' if current_state else '🔔 Yoqildi'}!")
        
        # Refresh the settings screen
        await notification_settings(callback, state)
        
    except Exception as e:
        logger.error(f"Error in toggle email notifications: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "account_info")
async def account_info(callback: CallbackQuery, state: FSMContext):
    """Show account information."""
    try:
        user_id = callback.from_user.id
        user = db.get_user(user_id)
        
        total_orders = db.get_user_orders_count(user_id)
        total_spent = db.get_user_total_spent(user_id)
        
        text = (
            "👤 Hisob Ma'lumotlari\n\n"
            f"👤 Ism: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}\n"
            f"📱 Username: @{user.get('username', 'N/A')}\n"
            f"📧 Telefon: {user.get('phone', 'Ko'rsatilmagan')}\n"
            f"📅 Qo'shilgan: {user.get('created_at', 'N/A')}\n\n"
            f"📦 Buyurtmalar: {total_orders}\n"
            f"💰 Jami xaraj qilgan: ${total_spent}\n"
            f"🎟️ Referral kodi: {user.get('referral_code', 'N/A')}\n"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("settings")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in account info: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "change_phone")
async def change_phone(callback: CallbackQuery, state: FSMContext):
    """Change phone number."""
    try:
        await state.set_state(UserStates.changing_phone)
        
        text = "📱 Yangi telefon raqamini kiriting:\n\nMisol: +998901234567"
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in change phone: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(UserStates.changing_phone)
async def process_change_phone(message: Message, state: FSMContext):
    """Process phone change."""
    try:
        phone = message.text.strip()
        user_id = message.from_user.id
        
        if len(phone) < 10:
            await message.answer("❌ Telefon raqami juda qisqa.")
            return
        
        db.update_user_phone(user_id, phone)
        
        await state.set_state(UserStates.in_settings)
        
        text = "✅ Telefon raqami muvaffaqiyatli o'zgartirildi!"
        await message.answer(
            text,
            reply_markup=get_back_keyboard("settings")
        )
        
    except Exception as e:
        logger.error(f"Error in process change phone: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "privacy_policy")
async def privacy_policy(callback: CallbackQuery, state: FSMContext):
    """Show privacy policy."""
    try:
        text = (
            "🔒 Maxfiylik Siyosati\n\n"
            "1. Ma'lumot Yig'ish\n"
            "Biz sizning shaxsiy ma'lumotlarni (ism, telefon, manzil) faqat buyurtma bajarilishi uchun yig'amiz.\n\n"
            "2. Ma'lumot Xavfsizligi\n"
            "Biz sizning ma'lumotlarini xavfsiz saqlashni va faqat taqdim etilgan maqsadda ishlashni ta'minlaymiz.\n\n"
            "3. Ma'lumotlardan Foydalanish\n"
            "Sizning ma'lumotlaridan faqat buyurtma bajarilishi va xizmat yaxshilash uchun foydalanamiz.\n\n"
            "4. Uchinchi Tomonlar\n"
            "Biz sizning ma'lumotlarini uchinchi tomonlarga bermaymiz.\n\n"
            "5. Haqlaringiz\n"
            "Siz istalgan vaqtda o'zingizning ma'lumotlarini o'zgartirishni yoki o'chirishni so'rashingiz mumkin.\n"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("settings")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in privacy policy: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "terms_of_service")
async def terms_of_service(callback: CallbackQuery, state: FSMContext):
    """Show terms of service."""
    try:
        text = (
            "📋 Xizmat Ko'rsatish Shartlari\n\n"
            "1. Buyurtma Qo'yish\n"
            "Siz 18 yoshdan yuqori bo'lishingiz kerak. Buyurtma o'z javobgarligingiz ostida qo'yiladi.\n\n"
            "2. To'lov\n"
            "To'lov faqat belgilangan usullar orqali qabul qilinadi. To'lovdan so'ng qaytarish qaytarish siyosatiga asosan amalga oshiriladi.\n\n"
            "3. Yetkazib Berish\n"
            "Biz belgilangan vaqtda yetkazib berishni harakat qilamiz, lekin garantiya bermaymiz.\n\n"
            "4. Qaytarish Siyosati\n"
            "Mahsulot sifati bo'yicha muammolar bo'lsa, 7 kun ichida qaytarish qabul qilinadi.\n\n"
            "5. Shartlarni Qabul Qilish\n"
            "Botdan foydalanish orqali siz ushbu shartlarni qabul qilasiz.\n"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("settings")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in terms of service: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "delete_account")
async def delete_account(callback: CallbackQuery, state: FSMContext):
    """Delete account confirmation."""
    try:
        await state.set_state(UserStates.confirming_delete_account)
        
        text = (
            "⚠️ Hisob O'chirish\n\n"
            "Buni amalga oshirish o'zgarmas! Barcha ma'lumotlaringiz o'chiriladi.\n\n"
            "Rostanmisiz?"
        )
        
        from keyboards import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Ha, o'chir", callback_data="confirm_delete_account")],
                [InlineKeyboardButton(text="❌ Yo'q, orqaga qayt", callback_data="settings")]
            ]
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in delete account: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "confirm_delete_account")
async def confirm_delete_account(callback: CallbackQuery, state: FSMContext):
    """Confirm delete account."""
    try:
        user_id = callback.from_user.id
        
        db.delete_user(user_id)
        
        await state.clear()
        
        text = "❌ Hisob o'chirildi.\n\nBotni yana ishlatsang, yangi hisob yaratiladi."
        await callback.message.edit_text(text)
        await callback.answer("✅ Hisob o'chirildi!")
        
    except Exception as e:
        logger.error(f"Error in confirm delete account: {e}")
        await callback.answer("❌ Xato yuz berdi.")
