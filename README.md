# Grocery Store Application

### Note: This project will be updated(Version-2) on 25th January, 2023 with major changes!!! 

```
What's new in Version-2:
->  Re-built the entire frontend using Vue3
->  Redis Caching
->  Updates to DB Model {Roles table: User(old), Admin(old) & Store Manager(new), Orders table(new)}
->  Celery Jobs
->  Token Based Authentication (previously Session Based)
->  And many more!
```

-  This is a project I did as part of my degree for this term(Version-2) so I can only upload after the project evaluation is done to avoid others from plagiarising my work
-  Version-1, which you currently see, is of previous term

## Description

In this project, I created a grocery store application that allows the user to add, remove, and update products in their cart to buy later.

The user can also view the total price of products in their cart and all the products in their cart.

The admin can add, view, remove, and update products, categories & units.

You can check the demonstration of this project in this video:  
https://drive.google.com/file/d/1Q40dHwBtHEI474PGyxoHfNT6_No-4Kpm/view?usp=sharing

## Features

User can:

-   Sign up and login
-   View all products, categories and all products in a category
-   Search for products/categories
-   Add products to their cart
-   View, update or delete items in their cart
-   Purchase all items in their cart

Admin can:

-   Only login
-   Add, view, update or delete products, categories & units

## Technologies used :

Flask, Bootstrap, Jinja2, SQLite

## Installation

1. Clone the repository
2. Create a virtual environment
3. Install dependencies from requirements.txt
4. Run the application

## Required packages

-   flask
-   Flask-SQLAlchemy
-   flask-login
-   flask_bcrypt
-   Pillow

## Project Structure

```bash
├── Code_21f1006486
    ├── Project Documentation.pdf
    └── Grocery Store
        ├── README.md
        ├── requirements.txt
        ├── app.py
        ├── instance
        │   └── database.sqlite3
        │
        └── application
            ├── __init__.py
            ├── models.py
            ├── views.py
            ├── auth_admin.py
            ├── auth_user.py
            ├── static
            │   ├── css
            │   │   └── style.css
            │   │
            │   └── images
            │
            └── templates
                ├── admin
                │   ├── admin_login.html
                │   ├── admin_view.html
                │   ├── category_pages
                │   │   ├── new_category.html
                │   │   ├── delete_category.html
                │   │   ├── edit_category.html
                │   │   ├── view_category.html
                │   │   └── category_list.html
                │   │
                │   ├── product_pages
                │   │   ├── new_product.html
                │   │   ├── delete_product.html
                │   │   ├── edit_product.html
                │   │   ├── view_product.html
                │   │   └── product_list.html
                │   │
                │   └── unit_pages
                │       ├── new_unit.html
                │       ├── delete_unit.html
                │       ├── edit_unit.html
                │       ├── view_unit.html
                │       └── unit_list.html
                │
                │
                ├── add_to_cart.html
                ├── all_categories.html
                ├── all_products.html
                ├── base.html
                ├── cart.html
                ├── category.html
                ├── home.html
                ├── login.html
                ├── product_section.html
                ├── product.html
                ├── purchase_all.html
                ├── purchase_cart.html
                ├── purchase_product.html
                ├── search_form.html
                ├── search_results.html
                ├── signup.html
                └── update_cart.html
```

##
