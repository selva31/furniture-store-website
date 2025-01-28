from flask_login import login_required, current_user
import random
from flask import Blueprint, render_template, redirect, url_for, flash, request,jsonify
from .models import Product, Cart, db,Wishlist,Order,OrderDetails
from sqlalchemy.orm import joinedload, subqueryload
import sqlalchemy
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    products = Product.query.all()
    random_products = products[:126]  # Display a subset of products

    wishlist = [item.product_id for item in Wishlist.query.filter_by(user_id=current_user.id).all()] if current_user.is_authenticated else []
    cart = [item.product_id for item in Cart.query.filter_by(user_id=current_user.id).all()] if current_user.is_authenticated else []

    return render_template('homepage.html', products=random_products, wishlist=wishlist, cart=cart)


@main.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = get_related_products(product)

    wishlist = [item.product_id for item in Wishlist.query.filter_by(user_id=current_user.id).all()] if current_user.is_authenticated else []
    cat = [item.product_id for item in Cart.query.filter_by(user_id=current_user.id).all()] if current_user.is_authenticated else []

    return render_template('product_details.html', product=product, related_products=related_products, wishlist=wishlist, cat=cat)

@main.route('/your_orders')
@login_required
def your_orders():
    try:
        orders = (OrderDetails.query
                  .filter_by(user_id=current_user.id)
                  .options(joinedload(OrderDetails.orders).joinedload(Order.product).joinedload(Product.images)) #Added image loading
                  .order_by(OrderDetails.order_date.desc())
                  .all())

        if not orders:
            flash("You haven't placed any orders yet.", "info")
            return render_template('your_orders.html', orders=[])

        return render_template('your_orders.html', orders=orders)
    except Exception as e:
        flash(f"An error occurred while fetching your orders: {e}", "danger")
        return redirect(url_for('main.home'))

def get_related_products(product, limit=5):
    """Finds related products based on category, then manufacturer and name."""
    if not product:
        return []

    # Exclude the current product
    query_criteria = [Product.id != product.id]

    # 1. Prioritize same category
    if product.category:
        query_criteria.append(Product.category == product.category)

    # 2. If same category, filter by manufacturer (only if there are products in the same category)
    #   The subquery counts matching products in the same category
    subquery = db.session.query(db.func.count(Product.id)).filter(
        Product.category == product.category, Product.id != product.id
    ).scalar()
    
    # if subquery > 0 and product.manufacturer:  #Only add manufacturer filter if same category products exist
    #     query_criteria.append(Product.manufacturer == product.manufacturer)

    if subquery > 0 and product.gender:  #Only add gender filter if same category products exist
        query_criteria.append(Product.gender == product.gender)
    # 3. If no match yet, filter by name similarity (least priority)
    name_parts = product.name.lower().split()  # Use the whole name for similarity
    if not any(isinstance(crit, sqlalchemy.sql.expression.BinaryExpression) for crit in query_criteria): #Check if criteria exist before adding name query
        name_query = " OR ".join([f"name LIKE '%{part}%'" for part in name_parts])
        query_criteria.append(db.text(name_query))


    related_products = (Product.query
                        .filter(*query_criteria)
                        .order_by(db.func.random()) #Add random ordering for diversity
                        .limit(12)
                        .all())

    return related_products



def calculate_tax(total_price):
    if total_price > 3000:
        return 0
    elif total_price > 2000:
        return 400
    elif total_price > 1000:
        return 200
    elif total_price > 500:
        return 100
    else:
        return 50
    
    
@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty!", "danger")
        return redirect(url_for('main.cart'))

    total_price = sum(item.total_price for item in cart_items)
    tax = calculate_tax(total_price)
    grand_total = total_price + tax

    if request.method == 'POST':
        city = request.form.get('city')
        address = request.form.get('address')
        name = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')

        # Input validation (basic example - enhance as needed)
        if not city or not address or not name or not email or not contact:
            flash("Please fill in all fields.", "danger")
            return render_template('checkout.html', cart_items=cart_items, total_price=total_price, tax=tax, grand_total=grand_total, city=current_user.city, address=current_user.address, name=current_user.username, email=current_user.email, contact=current_user.contact)

        if not contact.isdigit() or len(contact) != 10:
            flash("Invalid contact number.", "danger")
            return render_template('checkout.html', cart_items=cart_items, total_price=total_price, tax=tax, grand_total=grand_total, city=current_user.city, address=current_user.address, name=current_user.username, email=current_user.email, contact=current_user.contact)

        try:
            # Update user info (Consider email verification for security!)
            current_user.city = city
            current_user.address = address
            current_user.username = name
            current_user.email = email  # Email update - Implement verification!
            current_user.contact = contact
            db.session.commit()
            return redirect(url_for('main.place_order', name=name, email=email, contact=contact, city=city, address=address, total_price=total_price, tax=tax, grand_total=grand_total))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred updating user information: {e}", "danger")
            return render_template('checkout.html', cart_items=cart_items, total_price=total_price, tax=tax, grand_total=grand_total, city=current_user.city, address=current_user.address, name=current_user.username, email=current_user.email, contact=current_user.contact)

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, tax=tax, grand_total=grand_total, city=current_user.city, address=current_user.address, name=current_user.username, email=current_user.email, contact=current_user.contact)



@main.route('/place_order', methods=['GET', 'POST'])
@login_required
def place_order():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty!", "danger")
        return redirect(url_for('main.cart'))

    total_price = sum(item.total_price for item in cart_items)
    tax = calculate_tax(total_price)
    grand_total = total_price + tax

    # Get data from GET request (if redirected from checkout), or fallback to user data
    name = request.form.get('name')
    email = request.form.get('email')
    contact = request.form.get('contact')
    city = request.form.get('city')
    address = request.form.get('address')


    if not city or not address:
        flash("City and address are required.", "danger")
        return redirect(url_for('main.checkout')) # Redirect back to checkout if missing data


    try:
        # Create OrderDetails first
        order_details = OrderDetails(
            user_name=name,
            user_email=email,
            user_contact=contact,
            user_address=address,
            user_city=city,
            subtotal=total_price,
            delivery_charges=tax,
            grand_total=grand_total,
            order_date=datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(order_details)
        db.session.flush()  # Get the order_details ID
        order_details_id = order_details.id


        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product.quantity < item.quantity:
                flash(f"Insufficient stock for {product.name}!", "danger")
                return redirect(url_for('main.cart'))
            product.quantity -= item.quantity

            new_order = Order(
                order_details_id=order_details_id, # Use the OrderDetails ID
                product_id=item.product_id,
                quantity=item.quantity,
                order_amount=item.total_price,
                user_id=current_user.id
            )
            db.session.add(new_order)

        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash("Your order has been placed successfully!", "success")
        return redirect(url_for('main.home'))

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('main.checkout'))
 

@main.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    product = Product.query.get(product_id)

    if not product:
        flash("Product not found!", "danger")
        return redirect(request.referrer or url_for('main.home'))

    # Check if the product is already in the user's cart
    existing_cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if existing_cart_item:
        # Remove the product from the cart
        db.session.delete(existing_cart_item)
        db.session.commit()
        flash("Product removed from cart!", "success")
    else:
        # Add the product to the cart
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

@main.route('/update_cart_item/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart_item(cart_item_id):
    try:
        cart_item = Cart.query.get(cart_item_id)
        if not cart_item or cart_item.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Item not found or unauthorized'}), 400

        data = request.get_json()
        if not data or 'quantity' not in data:
            return jsonify({'success': False, 'error': 'Invalid request data'}), 400

        new_quantity = int(data['quantity'])
        product = cart_item.product # Get the associated product from cart_item

        if new_quantity < 1:
            return jsonify({'success': False, 'error': 'Quantity must be at least 1'}), 400
        if new_quantity > product.quantity: # Check for stock availability
            return jsonify({'success': False, 'error': f'Only {product.quantity} units in stock'}), 400


        cart_item.quantity = new_quantity
        cart_item.total_price = cart_item.quantity * cart_item.product.price
        db.session.commit()
        return jsonify({'success': True})

    except ValueError as e: #Catch specific errors for more informative messages
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Invalid quantity: {e}'}), 400
    except sqlalchemy.exc.IntegrityError as e: #Handle database errors
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Database error: {e}'}), 500
    except Exception as e:  # Catch any other exception
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An unexpected error occurred: {e}'}), 500
    
@main.route('/cart')
@login_required
def cart():
    cart_items = (Cart.query
                  .filter_by(user_id=current_user.id)
                  .options(joinedload(Cart.product).joinedload(Product.images)) # Eager load related objects
                  .all())

    # Filter out items where product is None
    valid_cart_items = [item for item in cart_items if item.product]


    product_stock = {}
    for item in valid_cart_items:
        if item.product:
            product_stock[item.product.id] = item.product.quantity

    return render_template('cart.html', cart_items=valid_cart_items, product_stock=product_stock)
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


@main.route('/wishlist', methods=['GET'])
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    for item in wishlist_items:
        try:
            item.product.discount = int(item.product.discount)
        except (ValueError, TypeError):
            item.product.discount = 0  # Handle cases where conversion fails
            print(f"WARNING: Invalid discount value for product {item.product.id}. Setting to 0.")

    return render_template('wishlist.html', wishlist_items=wishlist_items)


@main.route('/wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    product_id = request.form.get('product_id')
    product = Product.query.get(product_id)

    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for('main.home'))

    # Check if the product is already in the user's wishlist
    existing_wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if not existing_wishlist_item:
        wishlist_item = Wishlist(
            user_id=current_user.id,
            product_id=product.id
        )
        db.session.add(wishlist_item)
        db.session.commit()
        flash(f"'{product.name}' has been added to your wishlist!", "success")
    else:
        flash(f"'{product.name}' is already in your wishlist!", "info")

    return redirect(request.referrer or url_for('main.home'))


@main.route('/remove_from_wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    product_id = request.form.get('product_id')
    wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not wishlist_item:
        flash("Item not found in wishlist!", "danger")
        return redirect(request.referrer or url_for('main.home'))

    product_name = wishlist_item.product.name
    db.session.delete(wishlist_item)
    db.session.commit()
    flash(f"'{product_name}' has been removed from your wishlist!", "success")

    # Redirect to the referring page, or fallback to home
    referrer = request.referrer
    if referrer and "wishlist" not in referrer:  # Avoid looping back to the wishlist page itself
        return redirect(referrer)
    return redirect(url_for('main.home'))  # Fallback to home page



@main.context_processor
def inject_wishlist():
    """Inject the user's wishlist as a list of product IDs for easier checks in templates."""
    if current_user.is_authenticated:
        wishlist_ids = [item.product_id for item in Wishlist.query.filter_by(user_id=current_user.id).all()]
    else:
        wishlist_ids = []
    return dict(wishlist=wishlist_ids)



@main.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if query:
        search_results = Product.query.filter(
            Product.name.ilike(f'%{query}%') |
            Product.description.ilike(f'%{query}%') |
            Product.category.ilike(f'%{query}%')
        ).all()
    else:
        search_results = []
    
    wishlist = [item.product_id for item in Wishlist.query.filter_by(user_id=current_user.id).all()] if current_user.is_authenticated else []

    return render_template('search_results.html', products=search_results, query=query, wishlist=wishlist)
