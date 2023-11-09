from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user
from .models import User, Category, Product
from . import db
from datetime import datetime

views = Blueprint("views", __name__)


#Home page
@views.route("/")
def home():
    return render_template("home.html", user=current_user, ctgrs=Category.query.all(), products=Product.query.all())


#To search for products
@views.route("/search", methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    price = request.args.get('price')
    date_filter = request.args.get('date_filter')
    category_id = request.args.get('category_id')

    if not price and not date_filter and not category_id and not query:
        return redirect(url_for('views.home'))

    categories = None
    ctgrs = Category.query.all()
    products = Product.query

    if query:
        categories = Category.query
        categories = categories.filter(Category.category_name.contains(query))
        categories = categories.all()

        products = products.filter(Product.product_name.contains(query))


    if price:
        products = products.filter(Product.rate_per_unit <= float(price))

    if date_filter:
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
        products = products.filter(Product.manufacture_date >= date_filter)

    if category_id:
        products = products.filter(Product.category_id == category_id)
        
    products = products.all()

    return render_template("search_results.html", user=current_user, ctgrs=ctgrs, categories=categories, products=products, price=price, date_filter=date_filter, category_id=category_id, query=query)


#To view products of a particular category
@views.route("/category/<int:category_id>")
def view_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template("category.html", user=current_user, category=category, products=products)


#To view a particular product
@views.route("/product/<int:product_id>")
def view_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    return render_template("product.html", user=current_user, product=product)


#To view all categories
@views.route("/categories")
def categories():
    return render_template("all_categories.html", user=current_user, ctgrs=Category.query.all())


#To view all products
@views.route("/products")
def products():
    return render_template("all_products.html", user=current_user, products=Product.query.all())


