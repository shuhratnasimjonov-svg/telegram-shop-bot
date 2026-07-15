"""
Database module for the Telegram Shop Bot.
Handles all database operations using SQLAlchemy.
"""

import sqlite3
from datetime import datetime
from config import DATABASE_PATH
from logger import logger

class Database:
    """Database handler for the shop bot."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_db()
    
    def connect(self):
        """Create database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def init_db(self):
        """Initialize database tables."""
        self.connect()
        
        try:
            # Users table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language TEXT DEFAULT 'en',
                    is_subscribed INTEGER DEFAULT 0,
                    phone TEXT,
                    address TEXT,
                    referral_code TEXT UNIQUE,
                    referred_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Admin table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id INTEGER PRIMARY KEY,
                    username TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Categories table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Products table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    stock INTEGER DEFAULT 0,
                    image_urls TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)
            
            # Cart table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    UNIQUE(user_id, product_id)
                )
            """)
            
            # Orders table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    total_amount REAL NOT NULL,
                    phone TEXT,
                    address TEXT,
                    status TEXT DEFAULT 'pending',
                    promo_code TEXT,
                    discount_amount REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Order Items table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Promo Codes table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS promo_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    discount_type TEXT,
                    discount_value REAL NOT NULL,
                    max_uses INTEGER,
                    used_count INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            
            # Referrals table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    referred_id INTEGER NOT NULL,
                    bonus_amount REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                    FOREIGN KEY (referred_id) REFERENCES users(user_id)
                )
            """)
            
            # Spam protection table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS spam_protection (
                    user_id INTEGER PRIMARY KEY,
                    request_count INTEGER DEFAULT 0,
                    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned INTEGER DEFAULT 0,
                    banned_until TIMESTAMP
                )
            """)
            
            self.conn.commit()
            logger.info("✓ Database tables initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
        finally:
            self.close()
    
    # User operations
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, language: str = 'en', referral_code: str = None):
        """Add a new user to the database."""
        self.connect()
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name, language, referral_code)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, language, referral_code))
            self.conn.commit()
            logger.info(f"User {user_id} added to database")
        except sqlite3.Error as e:
            logger.error(f"Error adding user: {e}")
        finally:
            self.close()
    
    def get_user(self, user_id: int) -> dict:
        """Get user information by ID."""
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = self.cursor.fetchone()
            if user:
                columns = [description[0] for description in self.cursor.description]
                return dict(zip(columns, user))
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting user: {e}")
            return None
        finally:
            self.close()
    
    def update_user(self, user_id: int, **kwargs):
        """Update user information."""
        self.connect()
        try:
            updates = []
            values = []
            for key, value in kwargs.items():
                updates.append(f"{key} = ?")
                values.append(value)
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            logger.info(f"User {user_id} updated")
        except sqlite3.Error as e:
            logger.error(f"Error updating user: {e}")
        finally:
            self.close()
    
    # Category operations
    def add_category(self, name: str, description: str = None, image_url: str = None):
        """Add a new product category."""
        self.connect()
        try:
            self.cursor.execute("""
                INSERT INTO categories (name, description, image_url)
                VALUES (?, ?, ?)
            """, (name, description, image_url))
            self.conn.commit()
            category_id = self.cursor.lastrowid
            logger.info(f"Category '{name}' added with ID {category_id}")
            return category_id
        except sqlite3.Error as e:
            logger.error(f"Error adding category: {e}")
            return None
        finally:
            self.close()
    
    def get_categories(self):
        """Get all categories."""
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM categories ORDER BY name")
            categories = self.cursor.fetchall()
            columns = [description[0] for description in self.cursor.description]
            return [dict(zip(columns, cat)) for cat in categories]
        except sqlite3.Error as e:
            logger.error(f"Error getting categories: {e}")
            return []
        finally:
            self.close()
    
    # Product operations
    def add_product(self, category_id: int, name: str, description: str = None, 
                   price: float = 0, stock: int = 0, image_urls: str = None):
        """Add a new product."""
        self.connect()
        try:
            self.cursor.execute("""
                INSERT INTO products (category_id, name, description, price, stock, image_urls)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (category_id, name, description, price, stock, image_urls))
            self.conn.commit()
            product_id = self.cursor.lastrowid
            logger.info(f"Product '{name}' added with ID {product_id}")
            return product_id
        except sqlite3.Error as e:
            logger.error(f"Error adding product: {e}")
            return None
        finally:
            self.close()
    
    def get_products(self, category_id: int = None):
        """Get products, optionally filtered by category."""
        self.connect()
        try:
            if category_id:
                self.cursor.execute("""
                    SELECT * FROM products WHERE category_id = ? AND is_active = 1 
                    ORDER BY name
                """, (category_id,))
            else:
                self.cursor.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY name")
            
            products = self.cursor.fetchall()
            columns = [description[0] for description in self.cursor.description]
            return [dict(zip(columns, prod)) for prod in products]
        except sqlite3.Error as e:
            logger.error(f"Error getting products: {e}")
            return []
        finally:
            self.close()
    
    def get_product(self, product_id: int):
        """Get product by ID."""
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            product = self.cursor.fetchone()
            if product:
                columns = [description[0] for description in self.cursor.description]
                return dict(zip(columns, product))
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting product: {e}")
            return None
        finally:
            self.close()
    
    # Cart operations
    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1):
        """Add product to user's cart."""
        self.connect()
        try:
            self.cursor.execute("""
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?
            """, (user_id, product_id, quantity, quantity))
            self.conn.commit()
            logger.info(f"Product {product_id} added to cart for user {user_id}")
        except sqlite3.Error as e:
            logger.error(f"Error adding to cart: {e}")
        finally:
            self.close()
    
    def get_cart(self, user_id: int):
        """Get user's cart items."""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT c.id, c.product_id, c.quantity, p.name, p.price, p.image_urls
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
                ORDER BY c.added_at DESC
            """, (user_id,))
            
            items = self.cursor.fetchall()
            columns = [description[0] for description in self.cursor.description]
            return [dict(zip(columns, item)) for item in items]
        except sqlite3.Error as e:
            logger.error(f"Error getting cart: {e}")
            return []
        finally:
            self.close()
    
    def remove_from_cart(self, user_id: int, product_id: int):
        """Remove product from cart."""
        self.connect()
        try:
            self.cursor.execute("""
                DELETE FROM cart WHERE user_id = ? AND product_id = ?
            """, (user_id, product_id))
            self.conn.commit()
            logger.info(f"Product {product_id} removed from cart for user {user_id}")
        except sqlite3.Error as e:
            logger.error(f"Error removing from cart: {e}")
        finally:
            self.close()
    
    def clear_cart(self, user_id: int):
        """Clear user's entire cart."""
        self.connect()
        try:
            self.cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
            self.conn.commit()
            logger.info(f"Cart cleared for user {user_id}")
        except sqlite3.Error as e:
            logger.error(f"Error clearing cart: {e}")
        finally:
            self.close()
    
    # Order operations
    def create_order(self, user_id: int, total_amount: float, phone: str = None, 
                    address: str = None, promo_code: str = None, discount_amount: float = 0):
        """Create a new order."""
        self.connect()
        try:
            self.cursor.execute("""
                INSERT INTO orders (user_id, total_amount, phone, address, promo_code, discount_amount)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, total_amount, phone, address, promo_code, discount_amount))
            self.conn.commit()
            order_id = self.cursor.lastrowid
            logger.info(f"Order {order_id} created for user {user_id}")
            return order_id
        except sqlite3.Error as e:
            logger.error(f"Error creating order: {e}")
            return None
        finally:
            self.close()
    
    def add_order_item(self, order_id: int, product_id: int, quantity: int, price: float):
        """Add item to order."""
        self.connect()
        try:
            self.cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, price))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding order item: {e}")
        finally:
            self.close()
    
    def get_orders(self, user_id: int):
        """Get user's orders."""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC
            """, (user_id,))
            
            orders = self.cursor.fetchall()
            columns = [description[0] for description in self.cursor.description]
            return [dict(zip(columns, order)) for order in orders]
        except sqlite3.Error as e:
            logger.error(f"Error getting orders: {e}")
            return []
        finally:
            self.close()
    
    def update_order_status(self, order_id: int, status: str):
        """Update order status."""
        self.connect()
        try:
            self.cursor.execute("""
                UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (status, order_id))
            self.conn.commit()
            logger.info(f"Order {order_id} status updated to {status}")
        except sqlite3.Error as e:
            logger.error(f"Error updating order status: {e}")
        finally:
            self.close()
    
    # Promo code operations
    def add_promo_code(self, code: str, discount_type: str, discount_value: float, 
                       max_uses: int = None, expires_at: str = None):
        """Add a promo code."""
        self.connect()
        try:
            self.cursor.execute("""
                INSERT INTO promo_codes (code, discount_type, discount_value, max_uses, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (code.upper(), discount_type, discount_value, max_uses, expires_at))
            self.conn.commit()
            logger.info(f"Promo code '{code}' added")
        except sqlite3.Error as e:
            logger.error(f"Error adding promo code: {e}")
        finally:
            self.close()
    
    def get_promo_code(self, code: str):
        """Get promo code details."""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT * FROM promo_codes WHERE code = ? AND is_active = 1
            """, (code.upper(),))
            promo = self.cursor.fetchone()
            if promo:
                columns = [description[0] for description in self.cursor.description]
                return dict(zip(columns, promo))
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting promo code: {e}")
            return None
        finally:
            self.close()
    
    # Admin operations
    def add_admin(self, admin_id: int, username: str = None):
        """Add an admin."""
        self.connect()
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO admins (admin_id, username)
                VALUES (?, ?)
            """, (admin_id, username))
            self.conn.commit()
            logger.info(f"Admin {admin_id} added")
        except sqlite3.Error as e:
            logger.error(f"Error adding admin: {e}")
        finally:
            self.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin."""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT is_active FROM admins WHERE admin_id = ? AND is_active = 1
            """, (user_id,))
            result = self.cursor.fetchone()
            return result is not None
        except sqlite3.Error as e:
            logger.error(f"Error checking admin status: {e}")
            return False
        finally:
            self.close()


# Create database instance
db = Database()
