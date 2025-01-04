from flask_login import login_required, current_user
import random
from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import Product, Cart, db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    products = Product.query.all()

    # Optionally, shuffle the products to get a random order
    random.shuffle(products)

    # Limit the number of products displayed (optional)
    random_products = products[:18]  # Display 12 random products

    # Pass the products to the template
    return render_template('homepage.html', products=random_products)

@main.route('/product/<int:product_id>')
def product_details(product_id):
    # Fetch the product by ID
    product = Product.query.get_or_404(product_id)

    # Pass the product details to the template
    return render_template('product_details.html', product=product)

@main.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    product = Product.query.get(product_id)

    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for('main.home'))

    # Check if the product is already in the user's cart
    existing_cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if existing_cart_item:
        existing_cart_item.quantity += 1
        existing_cart_item.total_price = existing_cart_item.quantity * product.price
    else:
        cart_item = Cart(
            user_id=current_user.id,
            product_id=product.id,
            quantity=1,
            total_price=product.price
        )
        db.session.add(cart_item)

    db.session.commit()
    flash("Product added to cart!", "success")
    return redirect(request.referrer or url_for('main.home'))
    # return redirect(url_for('main.home'))


@main.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

@main.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    cart_item_id = request.form.get('cart_item_id')
    cart_item = Cart.query.get(cart_item_id)

    if not cart_item or cart_item.user_id != current_user.id:
        flash("Item not found or unauthorized!", "danger")
        return redirect(url_for('main.cart'))

    db.session.delete(cart_item)
    db.session.commit()
    flash("Item removed from cart!", "success")
    return redirect(url_for('main.cart'))
