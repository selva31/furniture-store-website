import sqlite3
from .models import *
from flask import Blueprint, render_template
category = Blueprint('category', __name__)

def product_view_by_category(category):
    """Fetch the products filtered by category."""
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
     # user_id = session.get('user_id', 1)
    user_id=1
    cursor.execute("SELECT id, name, manufacturer, price,  category, avg_rating FROM product where category = ?", (category,))
    products_by_category = cursor.fetchall()
    cart = cursor.execute(
        "SELECT product_id FROM cart WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    wishlist = cursor.execute(
        "SELECT product_id FROM wishlist WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    return products_by_category,[row[0] for row in wishlist],[row[0] for row in cart]

@category.route('/category/<category>')
def product_by_category(category):
    """Render the homepage by category filter."""
    products_by_category,stt,cat= product_view_by_category(category)
    return render_template('category.html', products_by_category=products_by_category,wis=stt,cat=cat)
