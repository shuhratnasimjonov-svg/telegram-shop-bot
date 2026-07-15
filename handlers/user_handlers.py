"""
User handlers for the Telegram Shop Bot.
Handles start command, main menu, and basic user interactions.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from states import UserStates
from keyboards import (
    get_start_keyboard, get_main_menu_keyboard, get_settings_keyboard,
    get_language_keyboard, get_support_keyboard, get_referral_keyboard
)
from database import db
from loader import bot
from logger import logger
import uuid

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    try:
        # Generate referral code if new user
        referral_code = f"ref_{user_id}_{str(uuid.uuid4())[:8]}"
        
        # Add user to database
        db.add_user(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            referral_code=referral_code
        )
        
        welcome_text = (
            f"👋 Assalomu alaykum, {first_name}!\n\n"
            "🛍️ Bizning online do'koniga xush kelibsiz!\n\n"
            "Siz quyidagilarni qila olasiz:\n"
            "• 🛒 Mahsulotlarni ko'rish va sotib olish\n"
            "• 📦 O'zingizning buyurtmalaringizni kuzatish\n"
            "• 👥 Do'stlaringizni taklif qiling va bonus oling\n"
            "• 💳 Qulay to'lov usullari\n\n"
            "Boshlaylik!"
        )
        
        await message.answer(welcome_text, reply_markup=get_start_keyboard())
        await state.set_state(UserStates.main_menu)
        
        logger.info(f"User {user_id} started the bot")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("❌ Xato yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.")


@router.message(F.text == "🛍️ Shop")
async def shop_command(message: Message, state: FSMContext):
    """Handle shop command."""
    try:
        await state.set_state(UserStates.viewing_categories)
        categories = db.get_categories()
        
        if not categories:
            await message.answer("❌ Kategoriyalar topilmadi.")
            return
        
        from keyboards import get_categories_keyboard
        
        text = "📂 Kategoriyalarni tanlang:"
        await message.answer(text, reply_markup=get_categories_keyboard(categories))
        
    except Exception as e:
        logger.error(f"Error in shop command: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(F.text == "🛒 Cart")
async def view_cart_command(message: Message, state: FSMContext):
    """Handle cart view command."""
    try:
        user_id = message.from_user.id
        await state.set_state(UserStates.viewing_cart)
        
        cart_items = db.get_cart(user_id)
        
        if not cart_items:
            await message.answer("🛒 Sizning savatingiz bo'sh.")
            return
        
        from keyboards import get_cart_keyboard
        
        total_price = sum(item['price'] * item['quantity'] for item in cart_items)
        
        text = "🛒 Sizning savatingiz:\n\n"
        for item in cart_items:
            text += f"• {item['name']}\n"
            text += f"  Miqdori: {item['quantity']} x ${item['price']} = ${item['price'] * item['quantity']}\n\n"
        
        text += f"💰 Jami: ${total_price}"
        
        await message.answer(text, reply_markup=get_cart_keyboard(cart_items))
        
    except Exception as e:
        logger.error(f"Error in cart command: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(F.text == "📦 Orders")
async def my_orders_command(message: Message, state: FSMContext):
    """Handle my orders command."""
    try:
        user_id = message.from_user.id
        await state.set_state(UserStates.viewing_orders)
        
        orders = db.get_orders(user_id)
        
        if not orders:
            await message.answer("📦 Sizda buyurtmalar yo'q.")
            return
        
        from keyboards import get_orders_keyboard
        
        text = "📦 Sizning buyurtmalaringiz:\n\n"
        
        await message.answer(text, reply_markup=get_orders_keyboard(orders))
        
    except Exception as e:
        logger.error(f"Error in orders command: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(F.text == "👥 Referral")
async def referral_command(message: Message, state: FSMContext):
    """Handle referral command."""
    try:
        user_id = message.from_user.id
        user = db.get_user(user_id)
        
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi.")
            return
        
        referral_code = user.get('referral_code', 'N/A')
        referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={referral_code}"
        
        text = (
            "👥 Referral Dasturi\n\n"
            "Do'stlaringizni taklif qiling va bonus oling!\n\n"
            f"🔗 Sizning referral linkingiz:\n"
            f"`{referral_link}`\n\n"
            "Bonus: Do'stingiz sotib olgan har bir buyurtmada 5% bonus oling!"
        )
        
        await message.answer(text, reply_markup=get_referral_keyboard(referral_code))
        
    except Exception as e:
        logger.error(f"Error in referral command: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(F.text == "⚙️ Settings")
async def settings_command(message: Message, state: FSMContext):
    """Handle settings command."""
    try:
        text = "⚙️ Sozlamalar"
        await message.answer(text, reply_markup=get_settings_keyboard())
        
    except Exception as e:
        logger.error(f"Error in settings command: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(F.text == "📞 Support")
async def support_command(message: Message, state: FSMContext):
    """Handle support command."""
    try:
        text = (
            "📞 Biz bilan bog'laning\n\n"
            "Agar sizda savollar yoki muammolar bo'lsa, "
            "iltimos biz bilan aloqaga chiqing."
        )
        await message.answer(text, reply_markup=get_support_keyboard())
        
    except Exception as e:
        logger.error(f"Error in support command: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "back_main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Go back to main menu."""
    try:
        await state.set_state(UserStates.main_menu)
        text = "🏠 Asosiy menyu"
        await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in back to main menu: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "change_language")
async def change_language(callback: CallbackQuery, state: FSMContext):
    """Show language selection."""
    try:
        text = "🌐 Tilni tanlang:"
        await callback.message.edit_text(text, reply_markup=get_language_keyboard())
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in change language: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery, state: FSMContext):
    """Select language."""
    try:
        lang = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        db.update_user(user_id, language=lang)
        
        lang_names = {"en": "English", "ru": "Русский", "uz": "Ўзбек"}
        
        await callback.answer(f"✅ Til {lang_names.get(lang)} ga o'zgartirildi!")
        await callback.message.edit_text(
            "⚙️ Sozlamalar",
            reply_markup=get_settings_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in select language: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery, state: FSMContext):
    """Handle settings callback."""
    try:
        text = "⚙️ Sozlamalar"
        await callback.message.edit_text(text, reply_markup=get_settings_keyboard())
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in settings callback: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery, state: FSMContext):
    """Handle support callback."""
    try:
        text = (
            "📞 Biz bilan bog'laning\n\n"
            "Agar sizda savollar yoki muammolar bo'lsa, "
            "iltimos biz bilan aloqaga chiqing."
        )
        await callback.message.edit_text(text, reply_markup=get_support_keyboard())
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in support callback: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "send_support_message")
async def send_support_message(callback: CallbackQuery, state: FSMContext):
    """Start support message."""
    try:
        text = "📝 O'zingizning muammongizni yozing:"
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in send support message: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message()
async def handle_text_message(message: Message, state: FSMContext):
    """Handle text messages."""
    try:
        current_state = await state.get_state()
        
        if current_state == UserStates.main_menu:
            await message.answer(
                "❓ Nima izlayapsiz? Iltimos, tugmalardan foydalaning.",
                reply_markup=get_start_keyboard()
            )
        else:
            await message.answer("❓ Nima izlayapsiz?")
            
    except Exception as e:
        logger.error(f"Error in text message handler: {e}")
        await message.answer("❌ Xato yuz berdi.")
