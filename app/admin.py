from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Product, Wishlist, OrderDetails, Cart, ProductImage
from . import db, bcrypt, mail
from .forms import ProductForm
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from werkzeug.utils import secure_filename
import os  # Make sure to import this module
from .utils import restrict_to_admin

admin = Blueprint('admin', __name__, url_prefix="/admin")

def create_admin_user():
    admin = User.query.filter_by(email='admin@gmail.com').first()
    if not admin:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        new_admin = User(
            username='admin',
            email='admin@gmail.com',
            password=hashed_password,
            role='admin',
        )
        db.session.add(new_admin)
        db.session.commit()

@admin.route('/admin_dashboard')
@restrict_to_admin()
def admin_dashboard():
    return render_template('admin_dashboard.html', username=current_user.username)

@admin.route('/view_products')
@restrict_to_admin()
def view_products():
    # Query all products from the database
    products = Product.query.all()
    return render_template('view_products.html', products=products)

@admin.route('/delete_product/<int:product_id>', methods=['POST'])
@restrict_to_admin()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    try:
        # Handle related cart items and wishlist items before deleting the product
        Cart.query.filter_by(product_id=product.id).delete()

        # Delete the wishlist items associated with the product
        Wishlist.query.filter_by(product_id=product.id).delete()
        # Delete related product images
        ProductImage.query.filter_by(product_id=product.id).delete()
        # Delete the product
        db.session.delete(product)
        db.session.commit()

        flash(f'Product "{product.name}" has been deleted successfully!', 'success')
        return redirect(url_for('admin.view_products'))

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the product: {str(e)}', 'danger')
        return redirect(url_for('admin.view_products'))

from werkzeug.utils import secure_filename
import os

@admin.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        # 1. Create the product object
        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            category=form.category.data,
            quantity=form.quantity.data,
            manufacturer=form.manufacturer.data,
            country_of_origin=form.country_of_origin.data,
            discount=form.discount.data,
            colour=form.colour.data,
        )

        db.session.add(product)
        db.session.flush()  # Ensures product.id is available before commit

        # 2. Handle image saving
        if form.images.data:
            for image_file in form.images.data:
                if image_file:
                    filename = secure_filename(image_file.filename)
                    save_path = os.path.join(current_app.config['IMAGE_UPLOAD_FOLDER'], filename)
                    image_file.save(save_path)

                    new_image = ProductImage(image_url=filename, product_id=product.id)
                    db.session.add(new_image)

        # 3. Handle 3D model saving
        if form.model.data:
            model_file = form.model.data
            model_filename = secure_filename(model_file.filename)
            model_path = os.path.join(current_app.config['MODEL_UPLOAD_FOLDER'], model_filename)
            model_file.save(model_path)
            product.model_file = model_filename

        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.view_products'))

    return render_template('add_product.html', form=form)



@admin.route('/update_product/<int:id>', methods=['GET', 'POST'])
@restrict_to_admin()
def update_product(id):
    # Fetch the product by its ID
    product = Product.query.get_or_404(id)

    form = ProductForm()

    if form.validate_on_submit():  # Check if form is valid on POST
        # Update the product details
        product.name = form.name.data
        product.price = form.price.data
        product.description = form.description.data
        product.colour = form.colour.data  # Update colour field
        product.category = form.category.data
        product.quantity = form.quantity.data
        product.manufacturer = form.manufacturer.data
        product.country_of_origin = form.country_of_origin.data
        product.discount = form.discount.data

        try:
            if form.image.data:
                image_filename = secure_filename(form.image.data.filename)
                image_path = os.path.join(current_app.root_path, "static", "upload")
                os.makedirs(image_path, exist_ok=True)
                form.image.data.save(os.path.join(image_path, image_filename))
                product.image = image_filename  # Update the image

            # Handle 3D model upload (.glb)
            if form.model.data:  # Assuming the form has a 'model' field
                model_filename = secure_filename(form.model.data.filename)
                model_path = os.path.join(current_app.root_path, "static", "models")
                os.makedirs(model_path, exist_ok=True)
                form.model.data.save(os.path.join(model_path, model_filename))
                product.model_path = f"static/models/{model_filename}"  # Update model path

            db.session.commit()
            flash(f'Product "{product.name}" has been updated successfully!', 'success')
            return redirect(url_for('admin.view_products'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating the product: {str(e)}', 'danger')
            return redirect(url_for('admin.update_product', id=id))  # Redirect to update page on error

    # Pre-populate the form with the current product data
    form.name.data = product.name
    form.price.data = product.price
    form.description.data = product.description
    form.category.data = product.category
    form.quantity.data = product.quantity
    form.colour.data = product.colour
    form.manufacturer.data = product.manufacturer
    form.country_of_origin.data = product.country_of_origin
    form.discount.data = product.discount

    return render_template('update_product.html', form=form, product=product)

@admin.route('/user_details', methods=['GET', 'POST'])
@restrict_to_admin()
def user_details():
    # Filters
    role_filter = request.args.get('role', '')
    location_filter = request.args.get('location', '')

    # Query to fetch user details with filters
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if location_filter:
        query = query.filter(User.city.ilike(f"%{location_filter}%"))

    users = query.all()

    return render_template('user_details.html', users=users, role_filter=role_filter, location_filter=location_filter)

@admin.route("/orders", methods=["GET"])
@restrict_to_admin()
def order_details():
    all_orders = db.session.query(OrderDetails).all()
    return render_template("all_orders.html", orders=all_orders)

@admin.route('/delete_user/<email>', methods=['POST'])
def delete_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'User with email {email} deleted successfully.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('admin.user_details'))
