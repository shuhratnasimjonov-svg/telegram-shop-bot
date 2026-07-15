"""
Cart handlers for the Telegram Shop Bot.
Handles shopping cart operations: view, add, remove, and checkout.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import UserStates
from keyboards import (
    get_cart_keyboard, get_checkout_keyboard, get_confirm_order_keyboard,
    get_back_keyboard
)
from database import db
from logger import logger
from datetime import datetime

router = Router()


@router.callback_query(F.data == "view_cart")
async def view_cart(callback: CallbackQuery, state: FSMContext):
    """View shopping cart."""
    try:
        user_id = callback.from_user.id
        await state.set_state(UserStates.viewing_cart)
        
        cart_items = db.get_cart(user_id)
        
        if not cart_items:
            await callback.answer("🛒 Sizning savatingiz bo'sh.")
            text = "🛒 Savatingiz bo'sh\n\nMahsulotlarni ko'rish uchun 🛍️ tugmasini bosing."
            await callback.message.edit_text(
                text,
                reply_markup=get_back_keyboard("shop")
            )
            return
        
        total_price = sum(item['price'] * item['quantity'] for item in cart_items)
        
        text = "🛒 Sizning savatingiz:\n\n"
        for i, item in enumerate(cart_items, 1):
            text += f"{i}. {item['name']}\n"
            text += f"   Miqdori: {item['quantity']} × ${item['price']} = ${item['price'] * item['quantity']}\n\n"
        
        text += f"💰 Jami: ${total_price}"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_cart_keyboard(cart_items)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in view cart: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("remove_cart_"))
async def remove_from_cart(callback: CallbackQuery, state: FSMContext):
    """Remove item from cart."""
    try:
        product_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        db.remove_from_cart(user_id, product_id)
        
        await callback.answer("✅ Mahsulot savatingizdan olib tashlandi!")
        
        # Refresh cart view
        cart_items = db.get_cart(user_id)
        
        if not cart_items:
            text = "🛒 Savatingiz bo'sh\n\nMahsulotlarni ko'rish uchun 🛍️ tugmasini bosing."
            await callback.message.edit_text(
                text,
                reply_markup=get_back_keyboard("shop")
            )
        else:
            total_price = sum(item['price'] * item['quantity'] for item in cart_items)
            
            text = "🛒 Sizning savatingiz:\n\n"
            for i, item in enumerate(cart_items, 1):
                text += f"{i}. {item['name']}\n"
                text += f"   Miqdori: {item['quantity']} × ${item['price']} = ${item['price'] * item['quantity']}\n\n"
            
            text += f"💰 Jami: ${total_price}"
            
            await callback.message.edit_text(
                text,
                reply_markup=get_cart_keyboard(cart_items)
            )
        
    except Exception as e:
        logger.error(f"Error in remove from cart: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery, state: FSMContext):
    """Clear entire cart."""
    try:
        user_id = callback.from_user.id
        
        db.clear_cart(user_id)
        
        await callback.answer("✅ Savatingiz tozalandi!")
        
        text = "🛒 Savatingiz bo'sh\n\nMahsulotlarni ko'rish uchun 🛍️ tugmasini bosing."
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("shop")
        )
        
    except Exception as e:
        logger.error(f"Error in clear cart: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery, state: FSMContext):
    """Start checkout process."""
    try:
        user_id = callback.from_user.id
        await state.set_state(UserStates.checkout)
        
        cart_items = db.get_cart(user_id)
        
        if not cart_items:
            await callback.answer("🛒 Savatingiz bo'sh!")
            return
        
        total_price = sum(item['price'] * item['quantity'] for item in cart_items)
        
        # Store checkout data
        await state.update_data(
            checkout_items=cart_items,
            checkout_total=total_price,
            phone=None,
            address=None,
            promo_code=None,
            promo_discount=0
        )
        
        text = (
            "💳 Checkout\n\n"
            f"📦 Mahsulotlar: {len(cart_items)} ta\n"
            f"💰 Jami: ${total_price}\n\n"
            "Quyidagi ma'lumotlarni to'ldiring:"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_checkout_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in checkout: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "enter_phone")
async def enter_phone_state(callback: CallbackQuery, state: FSMContext):
    """Ask for phone number."""
    try:
        text = "📞 O'zingizning telefon raqamingizni kiriting:\n\nMisol: +998901234567"
        await callback.message.edit_text(text)
        await state.set_state(UserStates.entering_phone)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in enter phone state: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(UserStates.entering_phone)
async def process_phone(message: Message, state: FSMContext):
    """Process phone number."""
    try:
        phone = message.text.strip()
        
        # Basic phone validation
        if len(phone) < 10:
            await message.answer("❌ Telefon raqami juda qisqa. Iltimos, to'g'ri raqam kiriting.")
            return
        
        await state.update_data(phone=phone)
        await state.set_state(UserStates.checkout)
        
        data = await state.get_data()
        total_price = data.get("checkout_total", 0)
        promo_discount = data.get("promo_discount", 0)
        final_total = total_price - promo_discount
        
        text = (
            "💳 Checkout\n\n"
            f"📞 Telefon: {phone}\n"
            f"💰 Jami: ${total_price}\n"
            f"🎟️ Chegirma: ${promo_discount}\n"
            f"✅ Oxirgi: ${final_total}\n\n"
            "Quyidagi ma'lumotlarni to'ldiring:"
        )
        
        await message.answer(
            text,
            reply_markup=get_checkout_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in process phone: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "enter_address")
async def enter_address_state(callback: CallbackQuery, state: FSMContext):
    """Ask for delivery address."""
    try:
        text = "📍 Yetkazib berish manzilini kiriting:"
        await callback.message.edit_text(text)
        await state.set_state(UserStates.entering_address)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in enter address state: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(UserStates.entering_address)
async def process_address(message: Message, state: FSMContext):
    """Process delivery address."""
    try:
        address = message.text.strip()
        
        if len(address) < 5:
            await message.answer("❌ Manzil juda qisqa. Iltimos, to'liq manzil kiriting.")
            return
        
        await state.update_data(address=address)
        await state.set_state(UserStates.checkout)
        
        data = await state.get_data()
        total_price = data.get("checkout_total", 0)
        promo_discount = data.get("promo_discount", 0)
        final_total = total_price - promo_discount
        phone = data.get("phone", "Kiritilmagan")
        
        text = (
            "💳 Checkout\n\n"
            f"📞 Telefon: {phone}\n"
            f"📍 Manzil: {address}\n"
            f"💰 Jami: ${total_price}\n"
            f"🎟️ Chegirma: ${promo_discount}\n"
            f"✅ Oxirgi: ${final_total}\n\n"
            "Quyidagi ma'lumotlarni to'ldiring:"
        )
        
        await message.answer(
            text,
            reply_markup=get_checkout_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in process address: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "apply_promo")
async def apply_promo_state(callback: CallbackQuery, state: FSMContext):
    """Ask for promo code."""
    try:
        text = "🎟️ Promo kodini kiriting:"
        await callback.message.edit_text(text)
        await state.set_state(UserStates.entering_promo_code)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in apply promo state: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(UserStates.entering_promo_code)
async def process_promo_code(message: Message, state: FSMContext):
    """Process promo code."""
    try:
        promo_code = message.text.strip().upper()
        
        # Check promo code in database
        promo = db.get_promo(promo_code)
        
        if not promo:
            await message.answer("❌ Bunday promo kod topilmadi.")
            await state.set_state(UserStates.checkout)
            return
        
        if promo['used_count'] >= promo['max_uses']:
            await message.answer("❌ Bu promo kod ishlatilmay qoldi.")
            await state.set_state(UserStates.checkout)
            return
        
        data = await state.get_data()
        total_price = data.get("checkout_total", 0)
        discount = (total_price * promo['discount_percent']) / 100
        
        await state.update_data(promo_code=promo_code, promo_discount=discount)
        await state.set_state(UserStates.checkout)
        
        final_total = total_price - discount
        
        text = (
            f"✅ Promo kod qabul qilindi!\n"
            f"🎟️ Kod: {promo_code}\n"
            f"💰 Chegirma: ${discount:.2f} ({promo['discount_percent']}%)\n"
            f"✅ Yangi total: ${final_total:.2f}\n\n"
            "Buyurtmangizni tasdiqlang yoki boshqa ma'lumotlarni o'zgartiring."
        )
        
        await message.answer(
            text,
            reply_markup=get_checkout_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in process promo code: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "confirm_order")
async def confirm_order_preview(callback: CallbackQuery, state: FSMContext):
    """Show order confirmation preview."""
    try:
        data = await state.get_data()
        
        phone = data.get("phone")
        address = data.get("address")
        
        if not phone or not address:
            await callback.answer("❌ Iltimos, telefon va manzilni kiriting!")
            return
        
        await state.set_state(UserStates.confirming_order)
        
        items = data.get("checkout_items", [])
        total_price = data.get("checkout_total", 0)
        promo_discount = data.get("promo_discount", 0)
        final_total = total_price - promo_discount
        promo_code = data.get("promo_code", "-")
        
        text = (
            "📋 Buyurtmani Tasdiqlash\n\n"
            "📦 Mahsulotlar:\n"
        )
        
        for item in items:
            text += f"• {item['name']} x{item['quantity']} = ${item['price'] * item['quantity']}\n"
        
        text += (
            f"\n📞 Telefon: {phone}\n"
            f"📍 Manzil: {address}\n"
            f"🎟️ Promo: {promo_code}\n\n"
            f"💰 Jami: ${total_price}\n"
            f"🎟️ Chegirma: ${promo_discount}\n"
            f"✅ Oxirgi: ${final_total}\n\n"
            "Buyurtmani tasdiqlaysizmi?"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_confirm_order_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in confirm order preview: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "confirm_final")
async def confirm_final_order(callback: CallbackQuery, state: FSMContext):
    """Finalize order."""
    try:
        user_id = callback.from_user.id
        data = await state.get_data()
        
        items = data.get("checkout_items", [])
        total_price = data.get("checkout_total", 0)
        promo_discount = data.get("promo_discount", 0)
        final_total = total_price - promo_discount
        phone = data.get("phone")
        address = data.get("address")
        promo_code = data.get("promo_code")
        
        # Create order in database
        order_id = db.create_order(
            user_id=user_id,
            items=items,
            total_amount=final_total,
            phone=phone,
            address=address,
            promo_code=promo_code,
            status="pending"
        )
        
        # Update promo code usage if applied
        if promo_code:
            db.increment_promo_usage(promo_code)
        
        # Clear cart
        db.clear_cart(user_id)
        
        await state.set_state(UserStates.main_menu)
        
        text = (
            "✅ Buyurtma muvaffaqiyatli yaratildi!\n\n"
            f"📋 Buyurtma raqami: #{order_id}\n"
            f"💰 Summa: ${final_total}\n"
            f"📊 Holat: Kutish rejimida\n\n"
            "Tez orada biz siz bilan bog'lanamiz.\n\n"
            "Rahmat, bizdan sotib olganingiz uchun!"
        )
        
        await callback.message.edit_text(text, reply_markup=get_back_keyboard("back_main_menu"))
        await callback.answer("✅ Buyurtma qabul qilindi!")
        
    except Exception as e:
        logger.error(f"Error in confirm final order: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Cancel order."""
    try:
        await state.set_state(UserStates.main_menu)
        
        text = "❌ Buyurtma bekor qilindi."
        await callback.message.edit_text(text, reply_markup=get_back_keyboard("back_main_menu"))
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in cancel order: {e}")
        await callback.answer("❌ Xato yuz berdi.")
