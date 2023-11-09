from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from . import db
from .models import User, Admin, Cart, Product, Category, Unit
from sqlalchemy.exc import IntegrityError


auth_user = Blueprint('auth_user', __name__)
bcrypt = Bcrypt()


@auth_user.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                session['user_type'] = 'user'
                return redirect(url_for('views.home'))
        else:
            flash('Check your username & password!', category='error')

    return render_template('login.html', user=current_user)


@auth_user.route('/singup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()
        admin = Admin.query.filter_by(admin_name=username).first()


        # Errors during signup

        if user and admin:
            flash('Username already exists.', category='error')
        elif len(username) < 3:
            flash('Username must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            new_user = User(username=username, password_hash=bcrypt.generate_password_hash(password1).decode('utf-8'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            session['user_type'] = 'user'
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
        
    return render_template('singup.html', user=current_user)


@auth_user.route('/logout')
@login_required
def logout():
    session.pop('user_type', None)
    logout_user()
    return redirect(url_for('views.home'))



##############################################################################################################
'''
                                USER CART OPERATIONS (CRUD)
'''
##############################################################################################################


# CREATE CART
@auth_user.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(product_id):
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except ValueError:
            flash('Invalid input', category='error')
            return redirect(url_for('views.home'))

        cart = Cart.query.filter_by(prod_id=product_id, user_id=current_user.id).first()

        try:
            db.session.begin_nested()

            if cart:
                cart.product_quantity += quantity
            else:
                cart = Cart(prod_id=product_id, product_quantity=quantity, user_id=current_user.id)
                db.session.add(cart)

            db.session.commit()

            flash('Product added to cart!', category='success')
            return redirect(url_for('auth_user.cart'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Error adding product to cart', category='error')
            return redirect(url_for('views.home'))

    return render_template('add_to_cart.html', user=current_user, product=Product.query.get(product_id))


# READ CART
@auth_user.route('/cart')
@login_required
def cart():
    carts = Cart.query.filter_by(user_id=int(current_user.id)).all()
    return render_template('cart.html', user=current_user, carts=carts)


# UPDATE CART
@auth_user.route('/update_cart/<int:cart_id>', methods=['GET', 'POST'])
@login_required
def update_cart(cart_id):
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        try:
            cart_id = int(cart_id)
            quantity = int(quantity)
        except ValueError:
            flash('Invalid input', category='error')
            return redirect(url_for('views.home'))

        cart = Cart.query.filter_by(id=cart_id, user_id=current_user.id).first()
        if not cart:
            flash('Product not found', category='error')
            return redirect(url_for('views.cart'))


        try:
            db.session.begin_nested()

            cart.product_quantity = quantity

            db.session.commit()

            flash('Cart updated!', category='success')
            return redirect(url_for('auth_user.cart'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Error updating cart', category='error')
            return redirect(url_for('views.home'))

    return render_template('update_cart.html', user=current_user, cart=Cart.query.get(cart_id))


# DELETE CART
@auth_user.route('/remove_from_cart/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    try:
        cart_id = int(cart_id)
    except ValueError:
        flash('Invalid input', category='error')
        return redirect(url_for('views.home'))

    cart = Cart.query.filter_by(id=cart_id, user_id=current_user.id).first()
    if not cart:
        flash('Product not found', category='error')
        return redirect(url_for('views.cart'))

    try:
        db.session.begin_nested()

        db.session.delete(cart)
        db.session.commit()

        flash('Product removed from cart!', category='success')
        return redirect(url_for('auth_user.cart'))
    
    except IntegrityError:
        db.session.rollback()
        flash('Error removing product from cart', category='error')
        return redirect(url_for('views.home'))


# DELETE ALL CART
@auth_user.route('/remove_all_from_cart')
@login_required
def remove_all_from_cart():
    carts = Cart.query.filter_by(user_id=current_user.id).all()
    if not carts:
        flash('Cart is empty', category='error')
        return redirect(url_for('views.cart'))
    
    try:
        db.session.begin_nested()

        for cart in carts:
            db.session.delete(cart)

        db.session.commit()

        flash('Cart is empty!', category='success')
        return redirect(url_for('auth_user.cart'))
    
    except IntegrityError:
        db.session.rollback()
        flash('Error removing products from cart', category='error')
        return redirect(url_for('views.home'))
    




##############################################################################################################
'''
                                USER PURCHASE OPERATIONS
'''
##############################################################################################################


# CART PRODUCT PURCHASE
@auth_user.route('/purchase/<int:cart_id>', methods=['GET', 'POST'])
@login_required
def purchase_cart(cart_id):
    if request.method == 'POST':
        try:
            cart_id = int(cart_id)
        except ValueError:
            flash('Invalid input', category='error')
            return redirect(url_for('views.home'))

        cart = Cart.query.filter_by(id=cart_id, user_id=current_user.id).first()
        if not cart:
            flash('Product not found', category='error')
            return redirect(url_for('views.cart'))

        try:
            db.session.begin_nested()

            product = Product.query.get(cart.prod_id)
            product.total_quantity -= cart.product_quantity

            db.session.delete(cart)
            db.session.commit()

            flash('Purchase successful!', category='success')
            return redirect(url_for('auth_user.cart'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Error purchasing product', category='error')
            return redirect(url_for('views.home'))

    return render_template('purchase_cart.html', user=current_user, cart=Cart.query.get(cart_id))


# CART PURCHASE
@auth_user.route('/purchase_all', methods=['GET', 'POST'])
@login_required
def purchase_all():
    if request.method == 'POST':
        carts = Cart.query.filter_by(user_id=current_user.id).all()
        if not carts:
            flash('Cart is empty', category='error')
            return redirect(url_for('views.cart'))

        

        try:
            db.session.begin_nested()

            for cart in carts:
                product = Product.query.get(cart.prod_id)
                product.total_quantity -= cart.product_quantity

                db.session.delete(cart)

            db.session.commit()

            flash('Purchase successful!', category='success')
            return redirect(url_for('views.home'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Error purchasing products', category='error')
            return redirect(url_for('views.home'))

    carts = Cart.query.filter_by(user_id=current_user.id).all()
    if not carts:
        flash('Cart is empty', category='error')
        return redirect(url_for('views.cart'))

    total_bill = 0
    for cart in carts:
        total_bill += cart.product_quantity * Product.query.get(cart.prod_id).rate_per_unit
    
    return render_template('purchase_all.html', user=current_user, carts=carts, total_bill=total_bill)


# DIRECT PRODUCT PURCHASE
@auth_user.route('/purchase_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def purchase_product(product_id):
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except ValueError:
            flash('Invalid input', category='error')
            return redirect(url_for('views.home'))

        product = Product.query.get(product_id)
        if not product:
            flash('Product not found', category='error')
            return redirect(url_for('views.home'))

        try:
            db.session.begin_nested()

            product.total_quantity -= quantity

            db.session.commit()

            flash('Purchase successful!', category='success')
            return redirect(url_for('auth_user.cart'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Error purchasing product', category='error')
            return redirect(url_for('views.home'))

    return render_template('purchase_product.html', user=current_user, product=Product.query.get(product_id))



