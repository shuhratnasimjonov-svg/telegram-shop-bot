"""
Order handlers for the Telegram Shop Bot.
Handles order viewing, tracking, and management.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states import UserStates
from keyboards import get_orders_keyboard, get_back_keyboard
from database import db
from logger import logger

router = Router()


@router.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery, state: FSMContext):
    """Show user's orders."""
    try:
        user_id = callback.from_user.id
        await state.set_state(UserStates.viewing_orders)
        
        orders = db.get_orders(user_id)
        
        if not orders:
            await callback.answer("📦 Sizda buyurtmalar yo'q.")
            text = "📦 Sizda hali buyurtmalar yo'q.\n\nMahsulotlarni sotib olish uchun 🛍️ tugmasini bosing."
            await callback.message.edit_text(
                text,
                reply_markup=get_back_keyboard("back_main_menu")
            )
            return
        
        text = "📦 Sizning buyurtmalaringiz:\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_orders_keyboard(orders, page=1)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in my orders: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("orders_page_"))
async def change_orders_page(callback: CallbackQuery, state: FSMContext):
    """Change orders page."""
    try:
        page = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        orders = db.get_orders(user_id)
        
        text = "📦 Sizning buyurtmalaringiz:\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_orders_keyboard(orders, page=page)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in change orders page: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("order_detail_"))
async def show_order_detail(callback: CallbackQuery, state: FSMContext):
    """Show order details."""
    try:
        order_id = int(callback.data.split("_")[2])
        await state.set_state(UserStates.viewing_order_detail)
        await state.update_data(current_order=order_id)
        
        order = db.get_order(order_id)
        
        if not order:
            await callback.answer("❌ Buyurtma topilmadi.")
            return
        
        # Status emoji mapping
        status_emoji = {
            "pending": "⏳",
            "confirmed": "✅",
            "shipped": "🚚",
            "delivered": "🎉",
            "cancelled": "❌"
        }
        
        status_text = {
            "pending": "Kutish rejimida",
            "confirmed": "Tasdiqlandi",
            "shipped": "Yuborildi",
            "delivered": "Yetkazildi",
            "cancelled": "Bekor qilindi"
        }
        
        status = order.get('status', 'pending')
        emoji = status_emoji.get(status, "❓")
        status_name = status_text.get(status, "Noma'lum")
        
        text = (
            f"📋 Buyurtma #{order_id}\n\n"
            f"{emoji} Holat: {status_name}\n"
            f"📅 Sana: {order.get('created_at', 'N/A')}\n"
            f"📞 Telefon: {order.get('phone', 'N/A')}\n"
            f"📍 Manzil: {order.get('address', 'N/A')}\n\n"
            f"📦 Mahsulotlar:\n"
        )
        
        items = order.get('items', [])
        total = 0
        for item in items:
            item_total = item.get('price', 0) * item.get('quantity', 1)
            total += item_total
            text += (
                f"• {item.get('name', 'N/A')}\n"
                f"  Miqdori: {item.get('quantity', 1)} × ${item.get('price', 0)} = ${item_total}\n"
            )
        
        text += (
            f"\n💰 Jami: ${order.get('total_amount', total)}\n"
            f"🎟️ Promo: {order.get('promo_code', '-')}\n\n"
            "Buyurtmani kuzatib turing yoki biz bilan bog'laning."
        )
        
        from keyboards import get_back_keyboard
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("my_orders")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in show order detail: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "referral")
async def referral_callback(callback: CallbackQuery, state: FSMContext):
    """Handle referral callback."""
    try:
        user_id = callback.from_user.id
        user = db.get_user(user_id)
        
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi.")
            return
        
        referral_code = user.get('referral_code', 'N/A')
        referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={referral_code}"
        
        # Get referral stats
        referrals = db.get_referrals(user_id)
        referral_count = len(referrals) if referrals else 0
        referral_bonus = referral_count * 5  # 5% per referral
        
        text = (
            "👥 Referral Dasturi\n\n"
            "Do'stlaringizni taklif qiling va bonus oling!\n\n"
            f"🔗 Sizning referral linkingiz:\n"
            f"`{referral_link}`\n\n"
            f"👥 Taklif qilinganlar: {referral_count}\n"
            f"💰 Jami bonus: ${referral_bonus}\n\n"
            "Bonus: Do'stingiz sotib olgan har bir buyurtmada 5% bonus oling!"
        )
        
        from keyboards import get_referral_keyboard
        
        await callback.message.edit_text(
            text,
            reply_markup=get_referral_keyboard(referral_code)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in referral callback: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "copy_referral_link")
async def copy_referral_link(callback: CallbackQuery, state: FSMContext):
    """Copy referral link."""
    try:
        user_id = callback.from_user.id
        user = db.get_user(user_id)
        
        referral_code = user.get('referral_code', 'N/A')
        referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={referral_code}"
        
        await callback.answer(f"✅ Link nusxalandi: {referral_link}")
        
    except Exception as e:
        logger.error(f"Error in copy referral link: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "my_referrals")
async def my_referrals(callback: CallbackQuery, state: FSMContext):
    """Show my referrals."""
    try:
        user_id = callback.from_user.id
        referrals = db.get_referrals(user_id)
        
        if not referrals:
            text = "👥 Siz hali do'st taklif qilmadingiz.\n\nReferral linkingizni ulashing va bonus oling!"
            await callback.message.edit_text(
                text,
                reply_markup=get_back_keyboard("referral")
            )
            await callback.answer()
            return
        
        text = "👥 Sizning taklif qilinganlar:\n\n"
        
        for i, referral in enumerate(referrals, 1):
            joined_date = referral.get('joined_date', 'N/A')
            purchase_count = referral.get('purchase_count', 0)
            text += (
                f"{i}. {referral.get('first_name', 'N/A')}\n"
                f"   📅 Qo'shilgan: {joined_date}\n"
                f"   📦 Buyurtmalar: {purchase_count}\n\n"
            )
        
        referral_count = len(referrals)
        referral_bonus = referral_count * 5
        text += f"\n💰 Jami bonus: ${referral_bonus}"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("referral")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in my referrals: {e}")
        await callback.answer("❌ Xato yuz berdi.")


# Admin order handlers

@router.callback_query(F.data == "admin_orders")
async def admin_view_orders(callback: CallbackQuery, state: FSMContext):
    """Admin: View all orders."""
    try:
        await state.set_state(UserStates.admin_viewing_orders)
        
        orders = db.get_all_orders()
        
        if not orders:
            text = "📦 Buyurtmalar yo'q."
            await callback.message.edit_text(text)
            return
        
        text = "📦 Barcha buyurtmalar:\n\n"
        
        for order in orders[:10]:  # Show first 10
            status_emoji = {
                "pending": "⏳",
                "confirmed": "✅",
                "shipped": "🚚",
                "delivered": "🎉",
                "cancelled": "❌"
            }
            status = order.get('status', 'pending')
            emoji = status_emoji.get(status, "❓")
            
            text += (
                f"{emoji} Buyurtma #{order['id']}\n"
                f"   Foydalanuvchi: {order.get('user_id', 'N/A')}\n"
                f"   Summa: ${order.get('total_amount', 0)}\n"
                f"   Sana: {order.get('created_at', 'N/A')}\n\n"
            )
        
        from keyboards import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back", callback_data="exit_admin")]
            ]
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in admin view orders: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("update_order_status_"))
async def update_order_status(callback: CallbackQuery, state: FSMContext):
    """Admin: Update order status."""
    try:
        parts = callback.data.split("_")
        order_id = int(parts[3])
        new_status = parts[4]
        
        db.update_order_status(order_id, new_status)
        
        status_text = {
            "pending": "Kutish rejimida",
            "confirmed": "Tasdiqlandi",
            "shipped": "Yuborildi",
            "delivered": "Yetkazildi",
            "cancelled": "Bekor qilindi"
        }
        
        await callback.answer(f"✅ Buyurtma statusi {status_text.get(new_status, 'yangilandi')}ga o'zgartirildi.")
        
    except Exception as e:
        logger.error(f"Error in update order status: {e}")
        await callback.answer("❌ Xato yuz berdi.")
