"""
FSM (Finite State Machine) states for the Telegram Shop Bot.
Defines all possible states for user interactions.
"""

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """User interaction states."""
    main_menu = State()
    viewing_categories = State()
    viewing_products = State()
    viewing_product_detail = State()
    adding_to_cart = State()
    viewing_cart = State()
    checkout = State()
    entering_phone = State()
    entering_address = State()
    confirming_order = State()
    entering_promo_code = State()
    viewing_orders = State()


class AdminStates(StatesGroup):
    """Admin panel states."""
    admin_menu = State()
    managing_products = State()
    adding_product = State()
    entering_product_name = State()
    entering_product_price = State()
    entering_product_stock = State()
    entering_product_category = State()
    entering_product_description = State()
    entering_product_image = State()
    
    managing_categories = State()
    adding_category = State()
    entering_category_name = State()
    entering_category_description = State()
    
    managing_promos = State()
    adding_promo = State()
    entering_promo_code = State()
    entering_promo_discount = State()
    entering_promo_max_uses = State()
    
    viewing_orders = State()
    updating_order_status = State()
    
    viewing_analytics = State()


class SubscriptionStates(StatesGroup):
    """Subscription verification states."""
    waiting_subscription = State()
    checking_subscription = State()


class ReferralStates(StatesGroup):
    """Referral system states."""
    viewing_referral_info = State()
    sharing_referral_link = State()
