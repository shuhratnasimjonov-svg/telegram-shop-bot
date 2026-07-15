"""
Product handlers for the Telegram Shop Bot.
Handles product browsing, viewing details, and adding to cart.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states import UserStates
from keyboards import (
    get_categories_keyboard, get_products_keyboard, get_product_detail_keyboard,
    get_quantity_keyboard, get_back_keyboard
)
from database import db
from logger import logger

router = Router()


@router.callback_query(F.data.startswith("category_"))
async def show_products(callback: CallbackQuery, state: FSMContext):
    """Show products in selected category."""
    try:
        category_id = int(callback.data.split("_")[1])
        await state.set_state(UserStates.viewing_products)
        await state.update_data(current_category=category_id, current_page=1)
        
        products = db.get_products_by_category(category_id)
        
        if not products:
            await callback.answer("❌ Bu kategoriyada mahsulotlar topilmadi.")
            return
        
        text = "📦 Mahsulotlarni tanlang:"
        await callback.message.edit_text(
            text,
            reply_markup=get_products_keyboard(products, page=1)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in show products: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("products_page_"))
async def change_products_page(callback: CallbackQuery, state: FSMContext):
    """Change product page."""
    try:
        page = int(callback.data.split("_")[2])
        data = await state.get_data()
        category_id = data.get("current_category")
        
        products = db.get_products_by_category(category_id)
        
        text = "📦 Mahsulotlarni tanlang:"
        await callback.message.edit_text(
            text,
            reply_markup=get_products_keyboard(products, page=page)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in change products page: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery, state: FSMContext):
    """Show product details."""
    try:
        product_id = int(callback.data.split("_")[1])
        await state.set_state(UserStates.viewing_product_detail)
        await state.update_data(current_product=product_id)
        
        product = db.get_product(product_id)
        
        if not product:
            await callback.answer("❌ Mahsulot topilmadi.")
            return
        
        text = (
            f"📦 {product['name']}\n\n"
            f"💰 Narx: ${product['price']}\n"
            f"📊 Qolgan: {product['stock']} ta\n"
            f"📂 Kategoriya: {product['category']}\n\n"
            f"📝 Tavsif:\n{product['description']}\n"
        )
        
        # Show product image if available
        if product.get('image'):
            try:
                await callback.message.delete()
                await callback.message.chat.send_photo(
                    photo=product['image'],
                    caption=text,
                    reply_markup=get_product_detail_keyboard(product_id)
                )
            except:
                await callback.message.edit_text(
                    text,
                    reply_markup=get_product_detail_keyboard(product_id)
                )
        else:
            await callback.message.edit_text(
                text,
                reply_markup=get_product_detail_keyboard(product_id)
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in show product detail: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart_handler(callback: CallbackQuery, state: FSMContext):
    """Handle add to cart button."""
    try:
        parts = callback.data.split("_")
        product_id = int(parts[3])
        
        await state.set_state(UserStates.adding_to_cart)
        await state.update_data(product_to_add=product_id)
        
        text = "🔢 Miqdorni tanlang:"
        await callback.message.edit_text(
            text,
            reply_markup=get_quantity_keyboard(product_id)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in add to cart handler: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data.startswith("quantity_"))
async def select_quantity(callback: CallbackQuery, state: FSMContext):
    """Select quantity and add to cart."""
    try:
        parts = callback.data.split("_")
        product_id = int(parts[1])
        quantity = int(parts[2])
        
        user_id = callback.from_user.id
        product = db.get_product(product_id)
        
        if not product:
            await callback.answer("❌ Mahsulot topilmadi.")
            return
        
        if quantity > product['stock']:
            await callback.answer(f"❌ Faqat {product['stock']} ta mavjud!")
            return
        
        # Add to cart
        db.add_to_cart(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        
        await state.set_state(UserStates.viewing_product_detail)
        
        text = (
            f"✅ {quantity} ta {product['name']} savatingizga qo'shildi!\n\n"
            f"💰 Narx: ${product['price'] * quantity}\n\n"
            "Quyidagilarni qila olasiz:"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_product_detail_keyboard(product_id)
        )
        await callback.answer("✅ Savatingizga qo'shildi!")
        
    except Exception as e:
        logger.error(f"Error in select quantity: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "cancel_quantity")
async def cancel_quantity(callback: CallbackQuery, state: FSMContext):
    """Cancel quantity selection."""
    try:
        data = await state.get_data()
        product_id = data.get("current_product")
        
        await state.set_state(UserStates.viewing_product_detail)
        
        product = db.get_product(product_id)
        
        text = (
            f"📦 {product['name']}\n\n"
            f"💰 Narx: ${product['price']}\n"
            f"📊 Qolgan: {product['stock']} ta\n"
            f"📂 Kategoriya: {product['category']}\n\n"
            f"📝 Tavsif:\n{product['description']}\n"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_product_detail_keyboard(product_id)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in cancel quantity: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "back_products")
async def back_to_products(callback: CallbackQuery, state: FSMContext):
    """Go back to products list."""
    try:
        data = await state.get_data()
        category_id = data.get("current_category")
        page = data.get("current_page", 1)
        
        await state.set_state(UserStates.viewing_products)
        
        products = db.get_products_by_category(category_id)
        
        text = "📦 Mahsulotlarni tanlang:"
        await callback.message.edit_text(
            text,
            reply_markup=get_products_keyboard(products, page=page)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in back to products: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "back_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Go back to categories list."""
    try:
        await state.set_state(UserStates.viewing_categories)
        
        categories = db.get_categories()
        
        text = "📂 Kategoriyalarni tanlang:"
        await callback.message.edit_text(
            text,
            reply_markup=get_categories_keyboard(categories)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in back to categories: {e}")
        await callback.answer("❌ Xato yuz berdi.")


@router.callback_query(F.data == "shop")
async def shop_callback(callback: CallbackQuery, state: FSMContext):
    """Handle shop callback."""
    try:
        await state.set_state(UserStates.viewing_categories)
        
        categories = db.get_categories()
        
        if not categories:
            await callback.answer("❌ Kategoriyalar topilmadi.")
            return
        
        text = "📂 Kategoriyalarni tanlang:"
        await callback.message.edit_text(
            text,
            reply_markup=get_categories_keyboard(categories)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in shop callback: {e}")
        await callback.answer("❌ Xato yuz berdi.")
