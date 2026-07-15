"""
Keyboards module for the Telegram Shop Bot.
Contains all inline and reply keyboards used in the bot.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import PRODUCTS_PER_PAGE, CATEGORIES_PER_PAGE


# Start menu keyboard
def get_start_keyboard():
    """Get start menu keyboard."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍️ Shop")],
            [KeyboardButton(text="🛒 Cart"), KeyboardButton(text="📦 Orders")],
            [KeyboardButton(text="👥 Referral"), KeyboardButton(text="⚙️ Settings")],
            [KeyboardButton(text="📞 Support")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


# Main menu inline keyboard
def get_main_menu_keyboard():
    """Get main menu inline keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Shop", callback_data="shop")],
            [InlineKeyboardButton(text="🛒 View Cart", callback_data="view_cart")],
            [InlineKeyboardButton(text="📦 My Orders", callback_data="my_orders")],
            [InlineKeyboardButton(text="👥 Referral Program", callback_data="referral")],
            [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton(text="📞 Support", callback_data="support")]
        ]
    )
    return keyboard


# Categories keyboard
def get_categories_keyboard(categories):
    """Get categories selection keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for i in range(0, len(categories), 2):
        row = []
        for j in range(2):
            if i + j < len(categories):
                cat = categories[i + j]
                row.append(InlineKeyboardButton(
                    text=cat['name'],
                    callback_data=f"category_{cat['id']}"
                ))
        keyboard.inline_keyboard.append(row)
    
    # Back button
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="⬅️ Back", callback_data="back_main_menu")
    ])
    
    return keyboard


# Products keyboard
def get_products_keyboard(products, page=1):
    """Get products selection keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    start = (page - 1) * PRODUCTS_PER_PAGE
    end = start + PRODUCTS_PER_PAGE
    page_products = products[start:end]
    
    for product in page_products:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{product['name']} - ${product['price']}",
                callback_data=f"product_{product['id']}"
            )
        ])
    
    # Pagination
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀️ Previous", callback_data=f"products_page_{page - 1}"))
    if end < len(products):
        nav_row.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"products_page_{page + 1}"))
    
    if nav_row:
        keyboard.inline_keyboard.append(nav_row)
    
    # Back button
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="⬅️ Back", callback_data="back_categories")
    ])
    
    return keyboard


# Product detail keyboard
def get_product_detail_keyboard(product_id):
    """Get product detail keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕", callback_data=f"add_to_cart_{product_id}_1"),
                InlineKeyboardButton(text="Add to Cart", callback_data=f"add_to_cart_{product_id}_1"),
                InlineKeyboardButton(text="➕", callback_data=f"add_to_cart_{product_id}_1")
            ],
            [InlineKeyboardButton(text="🛒 View Cart", callback_data="view_cart")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_products")]
        ]
    )
    return keyboard


# Quantity selector keyboard
def get_quantity_keyboard(product_id):
    """Get quantity selector keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data=f"quantity_{product_id}_1"),
                InlineKeyboardButton(text="2", callback_data=f"quantity_{product_id}_2"),
                InlineKeyboardButton(text="3", callback_data=f"quantity_{product_id}_3"),
                InlineKeyboardButton(text="5", callback_data=f"quantity_{product_id}_5")
            ],
            [
                InlineKeyboardButton(text="10", callback_data=f"quantity_{product_id}_10"),
                InlineKeyboardButton(text="15", callback_data=f"quantity_{product_id}_15"),
                InlineKeyboardButton(text="20", callback_data=f"quantity_{product_id}_20"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_quantity")
            ]
        ]
    )
    return keyboard


# Cart keyboard
def get_cart_keyboard(cart_items):
    """Get cart items keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for item in cart_items:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"❌ {item['name']} (qty: {item['quantity']})",
                callback_data=f"remove_cart_{item['product_id']}"
            )
        ])
    
    keyboard.inline_keyboard.extend([
        [InlineKeyboardButton(text="🛍️ Continue Shopping", callback_data="shop")],
        [InlineKeyboardButton(text="💳 Checkout", callback_data="checkout")],
        [InlineKeyboardButton(text="🗑️ Clear Cart", callback_data="clear_cart")]
    ])
    
    return keyboard


# Checkout keyboard
def get_checkout_keyboard():
    """Get checkout keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Enter Phone", callback_data="enter_phone")],
            [InlineKeyboardButton(text="📍 Enter Address", callback_data="enter_address")],
            [InlineKeyboardButton(text="🎟️ Apply Promo Code", callback_data="apply_promo")],
            [InlineKeyboardButton(text="✅ Confirm Order", callback_data="confirm_order")],
            [InlineKeyboardButton(text="⬅️ Back to Cart", callback_data="view_cart")]
        ]
    )
    return keyboard


# Confirm order keyboard
def get_confirm_order_keyboard():
    """Get confirm order keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_final"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_order")
            ]
        ]
    )
    return keyboard


# Orders keyboard
def get_orders_keyboard(orders, page=1):
    """Get orders list keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    start = (page - 1) * 5
    end = start + 5
    page_orders = orders[start:end]
    
    for order in page_orders:
        status_emoji = "✅" if order['status'] == "completed" else "⏳" if order['status'] == "pending" else "🚚"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{status_emoji} Order #{order['id']} - ${order['total_amount']}",
                callback_data=f"order_detail_{order['id']}"
            )
        ])
    
    # Pagination
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀️ Previous", callback_data=f"orders_page_{page - 1}"))
    if end < len(orders):
        nav_row.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"orders_page_{page + 1}"))
    
    if nav_row:
        keyboard.inline_keyboard.append(nav_row)
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="⬅️ Back", callback_data="back_main_menu")
    ])
    
    return keyboard


# Settings keyboard
def get_settings_keyboard():
    """Get settings keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Change Language", callback_data="change_language")],
            [InlineKeyboardButton(text="📞 Contact Support", callback_data="support")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main_menu")]
        ]
    )
    return keyboard


# Language keyboard
def get_language_keyboard():
    """Get language selection keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
            ],
            [
                InlineKeyboardButton(text="🇺🇿 Ўзбек", callback_data="lang_uz")
            ],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="settings")]
        ]
    )
    return keyboard


# Referral keyboard
def get_referral_keyboard(referral_code):
    """Get referral keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Copy Link", callback_data="copy_referral_link")],
            [InlineKeyboardButton(text="📊 My Referrals", callback_data="my_referrals")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main_menu")]
        ]
    )
    return keyboard


# Contact support keyboard
def get_support_keyboard():
    """Get support keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Send Message", callback_data="send_support_message")],
            [InlineKeyboardButton(text="📞 Call Support", url="https://t.me/support_bot")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main_menu")]
        ]
    )
    return keyboard


# Admin menu keyboard
def get_admin_menu_keyboard():
    """Get admin panel menu keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Manage Products", callback_data="admin_products")],
            [InlineKeyboardButton(text="📂 Manage Categories", callback_data="admin_categories")],
            [InlineKeyboardButton(text="🎟️ Manage Promos", callback_data="admin_promos")],
            [InlineKeyboardButton(text="📋 View Orders", callback_data="admin_orders")],
            [InlineKeyboardButton(text="📊 Analytics", callback_data="admin_analytics")],
            [InlineKeyboardButton(text="⬅️ Exit Admin", callback_data="exit_admin")]
        ]
    )
    return keyboard


# Confirm action keyboard
def get_confirm_keyboard(action_id):
    """Get confirmation keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes", callback_data=f"confirm_{action_id}"),
                InlineKeyboardButton(text="❌ No", callback_data=f"cancel_{action_id}")
            ]
        ]
    )
    return keyboard


# Back to menu keyboard
def get_back_keyboard(callback):
    """Get back button keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Back", callback_data=callback)]]
    )
    return keyboard
