"""
Support handlers for the Telegram Shop Bot.
Handles customer support and FAQ.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import UserStates
from keyboards import get_support_keyboard, get_faq_keyboard, get_back_keyboard
from database import db
from logger import logger

router = Router()


@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery, state: FSMContext):
    """Show support menu."""
    try:
        await state.set_state(UserStates.in_support)
        
        text = (
            "💬 Qo'llab-Quvvatlash Xizmati\n\n"
            "Sizga qanday yordam kerak?\n\n"
            "• Buyurtma haqida savol\n"
            "• To'lov muammolari\n"
            "• Mahsulot haqida ma'lumot\n"
            "• Boshqa savol yoki muammo\n"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_support_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in support: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "faq")
async def faq(callback: CallbackQuery, state: FSMContext):
    """Show FAQ."""
    try:
        await state.set_state(UserStates.viewing_faq)
        
        text = (
            "❓ Tez-tez So'raladigan Savollar (FAQ)\n\n"
            "Quyidagi mavzulardan birini tanlang:"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_faq_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in FAQ: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("faq_"))
async def show_faq_item(callback: CallbackQuery, state: FSMContext):
    """Show specific FAQ item."""
    try:
        faq_type = callback.data.split("_")[1]
        
        faq_content = {
            "shipping": (
                "🚚 Yetkazib Berish\n\n"
                "❓ Yetkazib berish qancha vaqt oladi?\n"
                "✅ Odatda 2-5 ish kuni.\n\n"
                "❓ Yetkazib berish bepul?\n"
                "✅ 50$ dan yuqori buyurtmalar uchun bepul, pastda 5$ haq.\n\n"
                "❓ Yetkazib berish manzilini o'zgartira olamiz?\n"
                "✅ Buyurtma tasdiqlanishiga qadar o'zgartira olasiz.\n\n"
                "❓ Buyurtmamni kuzatib turishim mumkin?\n"
                "✅ Ha, \"Buyurtmalarim\" bo'limida kuzatib turishingiz mumkin.\n"
            ),
            "payment": (
                "💳 To'lov\n\n"
                "❓ Qanday to'lov usullari qabul qilinadi?\n"
                "✅ Kredit karta, debit karta, va Digital dompalar.\n\n"
                "❓ To'lov xavfsizmi?\n"
                "✅ Ha, biz SSL shifrlashdan foydalanamiz.\n\n"
                "❓ To'lovni qaytarishi mumkin?\n"
                "✅ Ha, buyurtma qaytarish siyosatiga asosan.\n\n"
                "❓ Naqd pul orqali to'lashim mumkin?\n"
                "✅ Hozircha yo'q, lekin tez orada qo'shiladi.\n"
            ),
            "returns": (
                "🔄 Qaytarish\n\n"
                "❓ Qaytarish muddati qancha?\n"
                "✅ Buyurtma olingandan keyin 7 kun ichida.\n\n"
                "❓ Qaytarish pulini qancha vaqtda qaytaradi?\n"
                "✅ 5-10 ish kun ichida.\n\n"
                "❓ Foydalanilgan mahsulotni qaytara olamiz?\n"
                "✅ Faqat ishlatilmagan, original qadoqda bo'lsa.\n\n"
                "❓ Qaytarish haqi bor?\n"
                "✅ Bizning xatosi bo'lsa yo'q, aks holda siz to'lasiz.\n"
            ),
            "account": (
                "👤 Hisob\n\n"
                "❓ Parolimni unutdim, nima qilishim kerak?\n"
                "✅ Parol tiklash tugmasini bosing (bot orqali qilish mumkin emas).\n\n"
                "❓ Hisob ma'lumotlarini o'zgartira olamiz?\n"
                "✅ Ha, Sozlamalar bo'limida.\n\n"
                "❓ Hisob o'chirib tashla mumkin?\n"
                "✅ Ha, lekin bu o'zgarmas amal!\n\n"
                "❓ Birdan ko'p hisob yaratsa bo'ladimi?\n"
                "✅ Ha, har bir Telegram akkaunt uchun.\n"
            ),
            "products": (
                "📦 Mahsulotlar\n\n"
                "❓ Mahsulot sifati to'g'rimi?\n"
                "✅ Ha, biz faqat sertifikatsiyalangan mahsulotlar sotamiz.\n\n"
                "❓ Mahsulot qaytadan stokda bo'ladimi?\n"
                "✅ Bilmaydi, lekin bildirishnoma qo'yishingiz mumkin.\n\n"
                "❓ Diskount yoki promo kod bor?\n"
                "✅ Ha, veb-saytimizda doimo yangi takliflar!\n\n"
                "❓ Wholesale narxi bor?\n"
                "✅ Ha, support bilan bog'laning.\n"
            )
        }
        
        content = faq_content.get(faq_type, "❓ Savol topilmadi.")
        
        await callback.message.edit_text(
            content,
            reply_markup=get_back_keyboard("faq")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in show FAQ item: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "contact_support")
async def contact_support(callback: CallbackQuery, state: FSMContext):
    """Start contact support."""
    try:
        await state.set_state(UserStates.contacting_support)
        
        text = (
            "📧 Qo'llab-Quvvatlash Xizmati\n\n"
            "Iltimos, savolingiz yoki muammoningizni tavsiflab yozing:\n\n"
            "⏱️ Javob 2-4 soat ichida kutib turing."
        )
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in contact support: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(UserStates.contacting_support)
async def process_support_message(message: Message, state: FSMContext):
    """Process support message."""
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        support_message = message.text
        
        # Save support ticket
        ticket_id = db.create_support_ticket(
            user_id=user_id,
            user_name=user_name,
            message=support_message,
            status="open"
        )
        
        await state.set_state(UserStates.main_menu)
        
        text = (
            f"✅ Sizning so'roving qabul qilindi!\n\n"
            f"🎫 Ticket ID: {ticket_id}\n\n"
            "Qo'llab-quvvatlash jamoasi tez orada sizga javob beradi."
        )
        
        await message.answer(
            text,
            reply_markup=get_back_keyboard("back_main_menu")
        )
        
        # Notify support team (admin)
        admin_text = (
            f"📧 Yangi Support Ticket\n\n"
            f"🎫 Ticket ID: {ticket_id}\n"
            f"👤 Foydalanuvchi: {user_name} (ID: {user_id})\n"
            f"⏰ Vaqt: {message.date}\n\n"
            f"📝 Xabar:\n{support_message}"
        )
        
        # Send to support group (you need to set this up)
        logger.info(f"Support ticket created: {ticket_id}")
        
    except Exception as e:
        logger.error(f"Error in process support message: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "order_issue")
async def order_issue(callback: CallbackQuery, state: FSMContext):
    """Handle order issue."""
    try:
        await state.set_state(UserStates.reporting_order_issue)
        
        user_id = callback.from_user.id
        orders = db.get_orders(user_id)
        
        if not orders:
            await callback.answer("📦 Sizda buyurtmalar yo'q.")
            return
        
        text = "📦 Buyurtma Muammosi\n\n"
        text += "Qaysi buyurtma haqida muammo bor? Buyurtma raqamini kiriting:\n\n"
        
        for order in orders[-5:]:  # Show last 5 orders
            text += f"• Buyurtma #{order['id']} - ${order['total_amount']}\n"
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in order issue: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(UserStates.reporting_order_issue)
async def process_order_issue(message: Message, state: FSMContext):
    """Process order issue."""
    try:
        try:
            order_id = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Iltimos, to'g'ri buyurtma raqamini kiriting.")
            return
        
        user_id = message.from_user.id
        order = db.get_order(order_id)
        
        if not order or order.get('user_id') != user_id:
            await message.answer("❌ Buyurtma topilmadi yoki u sizga tegishli emas.")
            return
        
        await state.set_state(UserStates.describing_order_issue)
        await state.update_data(issue_order_id=order_id)
        
        text = (
            f"📦 Buyurtma #{order_id}\n\n"
            "Muammoni tavsiflab yozing:"
        )
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in process order issue: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(UserStates.describing_order_issue)
async def process_issue_description(message: Message, state: FSMContext):
    """Process issue description."""
    try:
        data = await state.get_data()
        order_id = data.get('issue_order_id')
        user_id = message.from_user.id
        issue_description = message.text
        
        # Create issue ticket
        ticket_id = db.create_support_ticket(
            user_id=user_id,
            user_name=message.from_user.first_name,
            message=f"Buyurtma muammosi #{order_id}: {issue_description}",
            status="open",
            order_id=order_id
        )
        
        await state.set_state(UserStates.main_menu)
        
        text = (
            f"✅ Muammo qabul qilindi!\n\n"
            f"🎫 Ticket ID: {ticket_id}\n"
            f"📦 Buyurtma: #{order_id}\n\n"
            "Bizning jamoa tez orada sizga javob beradi."
        )
        
        await message.answer(
            text,
            reply_markup=get_back_keyboard("back_main_menu")
        )
        
    except Exception as e:
        logger.error(f"Error in process issue description: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "live_chat")
async def live_chat(callback: CallbackQuery, state: FSMContext):
    """Live chat with support."""
    try:
        text = (
            "💬 Jonli Chat\n\n"
            "Hozir mavjud bo'lgan operatorlar:\n\n"
            "🟢 Ahmad - Online\n"
            "🟢 Fatima - Online\n\n"
            "Shuningdek, @support_bot orqali ham bog'lana olasiz."
        )
        
        from keyboards import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💬 Xat yubor", callback_data="send_live_chat_message")],
                [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="support")]
            ]
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in live chat: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "send_live_chat_message")
async def send_live_chat_message(callback: CallbackQuery, state: FSMContext):
    """Send live chat message."""
    try:
        await state.set_state(UserStates.sending_live_chat)
        
        text = "💬 Xabaringizni yozing:"
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in send live chat message: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(UserStates.sending_live_chat)
async def process_live_chat_message(message: Message, state: FSMContext):
    """Process live chat message."""
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        chat_message = message.text
        
        # Save chat message
        db.save_chat_message(
            user_id=user_id,
            user_name=user_name,
            message=chat_message
        )
        
        await state.set_state(UserStates.main_menu)
        
        text = "✅ Xabar yuborildi!\n\nOperator tez orada sizga javob beradi."
        
        await message.answer(
            text,
            reply_markup=get_back_keyboard("back_main_menu")
        )
        
    except Exception as e:
        logger.error(f"Error in process live chat message: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "feedback")
async def feedback(callback: CallbackQuery, state: FSMContext):
    """Send feedback."""
    try:
        await state.set_state(UserStates.sending_feedback)
        
        text = (
            "⭐ Fikr-Mulohaza\n\n"
            "Bizning xizmati haqida fikringizni bilishga qiziqamiz.\n\n"
            "Iltimos, sizning fikringizni yozing:"
        )
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in feedback: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(UserStates.sending_feedback)
async def process_feedback(message: Message, state: FSMContext):
    """Process feedback."""
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        feedback_text = message.text
        
        # Save feedback
        db.save_feedback(
            user_id=user_id,
            user_name=user_name,
            feedback=feedback_text
        )
        
        await state.set_state(UserStates.main_menu)
        
        text = (
            "✅ Fikr-mulohaza jo'natildi!\n\n"
            "Diqqatingiz uchun rahmat. Sizning fikringiz bizga juda muhim!"
        )
        
        await message.answer(
            text,
            reply_markup=get_back_keyboard("back_main_menu")
        )
        
    except Exception as e:
        logger.error(f"Error in process feedback: {e}")
        await message.answer("❌ Xato yuz berdi.")
