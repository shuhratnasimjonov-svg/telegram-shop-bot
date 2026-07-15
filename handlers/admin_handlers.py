"""
Admin handlers for the Telegram Shop Bot.
Handles admin panel, product management, and analytics.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import UserStates, AdminStates
from keyboards import (
    get_admin_panel_keyboard, get_product_management_keyboard,
    get_category_management_keyboard, get_back_keyboard
)
from database import db
from logger import logger

router = Router()


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    """Show admin panel."""
    try:
        # Check if user is admin
        if not db.is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz.")
            return
        
        await state.set_state(AdminStates.in_admin_panel)
        
        # Get statistics
        total_users = db.get_total_users()
        total_orders = db.get_total_orders()
        total_revenue = db.get_total_revenue()
        pending_orders = db.get_pending_orders_count()
        
        text = (
            "🔧 Admin Panel\n\n"
            f"👥 Jami foydalanuvchilar: {total_users}\n"
            f"📦 Jami buyurtmalar: {total_orders}\n"
            f"⏳ Kutish rejimidagi buyurtmalar: {pending_orders}\n"
            f"💰 Jami kirim: ${total_revenue}\n\n"
            "Quyidagi amallardan birini tanlang:"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_panel_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in admin panel: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "manage_products")
async def manage_products(callback: CallbackQuery, state: FSMContext):
    """Product management menu."""
    try:
        await state.set_state(AdminStates.managing_products)
        
        text = "📦 Mahsulotlarni Boshqarish\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_product_management_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in manage products: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "add_product")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    """Start adding new product."""
    try:
        await state.set_state(AdminStates.adding_product_name)
        
        text = "📦 Yangi Mahsulot Qo'shish\n\n"
        text += "Mahsulotning nomini kiriting:"
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in add product start: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(AdminStates.adding_product_name)
async def process_product_name(message: Message, state: FSMContext):
    """Process product name."""
    try:
        product_name = message.text.strip()
        
        if len(product_name) < 3:
            await message.answer("❌ Mahsulot nomi juda qisqa. Minimum 3 belgi.")
            return
        
        await state.update_data(product_name=product_name)
        await state.set_state(AdminStates.adding_product_price)
        
        text = "💰 Mahsulotning narxini kiriting (masalan: 9.99):"
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in process product name: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(AdminStates.adding_product_price)
async def process_product_price(message: Message, state: FSMContext):
    """Process product price."""
    try:
        try:
            price = float(message.text.strip())
        except ValueError:
            await message.answer("❌ Iltimos, to'g'ri raqam kiriting.")
            return
        
        if price < 0:
            await message.answer("❌ Narx manfiy bo'lishi mumkin emas.")
            return
        
        await state.update_data(product_price=price)
        await state.set_state(AdminStates.adding_product_stock)
        
        text = "📊 Qolgan miqdorni kiriting:"
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in process product price: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(AdminStates.adding_product_stock)
async def process_product_stock(message: Message, state: FSMContext):
    """Process product stock."""
    try:
        try:
            stock = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Iltimos, to'g'ri raqam kiriting.")
            return
        
        if stock < 0:
            await message.answer("❌ Qolgan miqdor manfiy bo'lishi mumkin emas.")
            return
        
        await state.update_data(product_stock=stock)
        await state.set_state(AdminStates.adding_product_description)
        
        text = "📝 Mahsulotning tavsifini kiriting:"
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in process product stock: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(AdminStates.adding_product_description)
async def process_product_description(message: Message, state: FSMContext):
    """Process product description."""
    try:
        description = message.text.strip()
        
        if len(description) < 10:
            await message.answer("❌ Tavsif juda qisqa. Minimum 10 belgi.")
            return
        
        await state.update_data(product_description=description)
        await state.set_state(AdminStates.adding_product_category)
        
        categories = db.get_categories()
        
        text = "📂 Kategoriyani tanlang:\n\n"
        for i, cat in enumerate(categories, 1):
            text += f"{i}. {cat['name']}\n"
        
        text += f"\n{len(categories) + 1}. Yangi kategoriya qo'shish"
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in process product description: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(AdminStates.adding_product_category)
async def process_product_category(message: Message, state: FSMContext):
    """Process product category."""
    try:
        try:
            category_choice = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Iltimos, to'g'ri raqam kiriting.")
            return
        
        categories = db.get_categories()
        
        if 1 <= category_choice <= len(categories):
            category_id = categories[category_choice - 1]['id']
            await state.update_data(product_category_id=category_id)
        else:
            await state.set_state(AdminStates.adding_new_category_for_product)
            await message.answer("📂 Yangi kategoriya nomini kiriting:")
            return
        
        # Save product
        data = await state.get_data()
        
        product_id = db.add_product(
            name=data['product_name'],
            price=data['product_price'],
            stock=data['product_stock'],
            description=data['product_description'],
            category_id=data['product_category_id']
        )
        
        await state.set_state(AdminStates.in_admin_panel)
        
        text = f"✅ Mahsulot muvaffaqiyatli qo'shildi!\n\nMahsulot ID: {product_id}"
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in process product category: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.message(AdminStates.adding_new_category_for_product)
async def process_new_category(message: Message, state: FSMContext):
    """Process new category."""
    try:
        category_name = message.text.strip()
        
        if len(category_name) < 3:
            await message.answer("❌ Kategoriya nomi juda qisqa.")
            return
        
        category_id = db.add_category(category_name)
        await state.update_data(product_category_id=category_id)
        
        # Save product
        data = await state.get_data()
        
        product_id = db.add_product(
            name=data['product_name'],
            price=data['product_price'],
            stock=data['product_stock'],
            description=data['product_description'],
            category_id=category_id
        )
        
        await state.set_state(AdminStates.in_admin_panel)
        
        text = f"✅ Yangi kategoriya va mahsulot qo'shildi!\n\nMahsulot ID: {product_id}"
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in process new category: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "view_all_products")
async def view_all_products(callback: CallbackQuery, state: FSMContext):
    """View all products."""
    try:
        products = db.get_all_products()
        
        if not products:
            await callback.answer("❌ Mahsulotlar topilmadi.")
            return
        
        text = "📦 Barcha Mahsulotlar:\n\n"
        
        for i, product in enumerate(products[:10], 1):
            text += (
                f"{i}. {product['name']}\n"
                f"   Narx: ${product['price']}\n"
                f"   Qolgan: {product['stock']} ta\n\n"
            )
        
        if len(products) > 10:
            text += f"\n... va {len(products) - 10} ko'p mahsulot"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("manage_products")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in view all products: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "manage_categories")
async def manage_categories(callback: CallbackQuery, state: FSMContext):
    """Category management menu."""
    try:
        await state.set_state(AdminStates.managing_categories)
        
        text = "📂 Kategoriyalarni Boshqarish\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_category_management_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in manage categories: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    """Start adding new category."""
    try:
        await state.set_state(AdminStates.adding_category_name)
        
        text = "📂 Yangi Kategoriya Qo'shish\n\n"
        text += "Kategoriya nomini kiriting:"
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in add category start: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.message(AdminStates.adding_category_name)
async def process_category_name(message: Message, state: FSMContext):
    """Process category name."""
    try:
        category_name = message.text.strip()
        
        if len(category_name) < 3:
            await message.answer("❌ Kategoriya nomi juda qisqa.")
            return
        
        category_id = db.add_category(category_name)
        
        await state.set_state(AdminStates.in_admin_panel)
        
        text = f"✅ Kategoriya muvaffaqiyatli qo'shildi!\n\nKategoriya ID: {category_id}"
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error in process category name: {e}")
        await message.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "view_analytics")
async def view_analytics(callback: CallbackQuery, state: FSMContext):
    """View analytics."""
    try:
        analytics = db.get_analytics()
        
        text = (
            "📊 Analytics\n\n"
            f"👥 Jami foydalanuvchilar: {analytics.get('total_users', 0)}\n"
            f"📦 Jami buyurtmalar: {analytics.get('total_orders', 0)}\n"
            f"💰 Jami kirim: ${analytics.get('total_revenue', 0)}\n"
            f"⏳ Kutish rejimidagi buyurtmalar: {analytics.get('pending_orders', 0)}\n"
            f"🚚 Yuborilgan buyurtmalar: {analytics.get('shipped_orders', 0)}\n"
            f"🎉 Yetkazilgan buyurtmalar: {analytics.get('delivered_orders', 0)}\n"
            f"📱 O'rtacha buyurtma: ${analytics.get('average_order', 0)}\n"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("admin_panel")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in view analytics: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "user_management")
async def user_management(callback: CallbackQuery, state: FSMContext):
    """User management."""
    try:
        users = db.get_all_users()
        
        if not users:
            await callback.answer("❌ Foydalanuvchilar topilmadi.")
            return
        
        text = "👥 Foydalanuvchilar:\n\n"
        
        for i, user in enumerate(users[:10], 1):
            text += (
                f"{i}. {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}\n"
                f"   ID: {user.get('user_id', 'N/A')}\n"
                f"   Qo'shilgan: {user.get('created_at', 'N/A')}\n\n"
            )
        
        if len(users) > 10:
            text += f"\n... va {len(users) - 10} ko'p foydalanuvchi"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("admin_panel")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in user management: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "exit_admin")
async def exit_admin(callback: CallbackQuery, state: FSMContext):
    """Exit admin panel."""
    try:
        await state.set_state(UserStates.main_menu)
        
        text = "✅ Admin panelingizdan chiqdingiz."
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("back_main_menu")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in exit admin: {e}")
        await callback.answer("❌ Xato yuz berdi.")
