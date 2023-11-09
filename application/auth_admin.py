from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import secrets
import os
from PIL import Image
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from . import db
from .models import Admin, Category, Product, Unit


auth_admin = Blueprint('auth_admin', __name__)
bcrypt = Bcrypt()


############################################################################################################################

'''Save picture to static/images folder and return the filename'''
def save_picture(form_picture, pic_filename):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(pic_filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(auth_admin.root_path, 'static/images', picture_fn)

    output_size = (350, 350)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_picture(pic_filename):
    pic_path = os.path.join(auth_admin.root_path, 'static/images', pic_filename)

    try:
        os.remove(pic_path)
        print("% s removed successfully" % pic_path)
    except OSError as error:
        print(error)
        print("File path can not be removed")
        flash('Error occured while deleting image.', category='error')

############################################################################################################################


@auth_admin.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_name = request.form.get('admin_name')
        password = request.form.get('password')

        admin = Admin.query.filter_by(admin_name=admin_name).first()

        if admin:
            if bcrypt.check_password_hash(admin.password_hash, password):
                flash('Logged in successfully!', category='success')
                login_user(admin, remember=True)
                session['user_type'] = 'admin'
                return redirect(url_for('auth_admin.admin_view'))
            else:
                    flash('Incorrect password!', category='error')
        else:
            flash('Admin does not exist.', category='error')

    return render_template('admin/admin_login.html', user=current_user)

@auth_admin.route('/admin_logout')
@login_required
def admin_logout():
    session.pop('user_type', None)
    logout_user()
    return redirect(url_for('views.home'))


@auth_admin.route("/")  
@login_required
def admin_view():
    return render_template("admin/admin_view.html", user=current_user)



############################################################################################################################
'''
--------------------------------  LIST PAGES  --------------------------------
'''
############################################################################################################################


# Category list
@auth_admin.route('/category_list')
@login_required
def category_list():
    categories = Category.query.all()
    return render_template('admin/category_pages/category_list.html', categories=categories, user=current_user)


# Product list
@auth_admin.route('/product_list')
@login_required
def product_list():
    products = Product.query.all()
    return render_template('admin/product_pages/product_list.html', products=products, user=current_user)


# Unit list
@auth_admin.route('/unit_list')
@login_required
def unit_list():
    units = Unit.query.all()
    return render_template('admin/unit_pages/unit_list.html', units=units, user=current_user)



############################################################################################################################
'''
--------------------------------  CRUD FOR CATEGORY  --------------------------------
'''
############################################################################################################################


#Create new category
@auth_admin.route('/new_category', methods=['GET', 'POST'])
@login_required
def new_category():
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        category = Category.query.filter_by(category_name=category_name).first()

        if 'category_picture' not in request.files:
            flash('Upload an image.', category='error')
            return redirect(url_for('auth_admin.new_category'))
        category_picture = request.files['category_picture']
        pic_filename = secure_filename(category_picture.filename)


        if category:
            flash('Category already exists.', category='error')
            return redirect(url_for('auth_admin.new_category'))
        
        
        # Category name is checked below
        elif len(category_name) < 3:
            flash('Category must be greater than 2 characters.', category='error')
            return redirect(url_for('auth_admin.new_category'))
        
        elif len(category_name) > 40:
            flash('Category must be less than 40 characters.', category='error')
            return redirect(url_for('auth_admin.new_category'))
        

        # Category picture is checked below
        elif pic_filename == '':
            flash('No selected file.', category='error')
            return redirect(url_for('auth_admin.new_category'))
        
        elif not allowed_file(pic_filename):
            flash('File type must be svg, webp, png, jpg or jpeg.', category='error')
            return redirect(url_for('auth_admin.new_category'))
        
        
        else:
            try:
                db.session.begin_nested()

                new_category = Category(category_name=category_name)
                new_pic_filename = save_picture(category_picture, pic_filename)
                new_category.category_picture = new_pic_filename

                db.session.add(new_category)
                db.session.commit()

                flash('Category created!', category='success')
                new_cat = Category.query.filter_by(category_name=category_name).first()
                return redirect(url_for('auth_admin.view_category', category_id=new_cat.id))
            
            except IntegrityError:
                db.session.rollback()
                flash('Something went wrong.', category='error')
                return redirect(url_for('auth_admin.new_category'))
            
            finally:
                db.session.close()
       
                
    return render_template('admin/category_pages/new_category.html', user=current_user)

# Read category
@auth_admin.route('/view_category/<int:category_id>')
@login_required
def view_category(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template('admin/category_pages/view_category.html', user=current_user, category=category)
    
# Update category
@auth_admin.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get(category_id)

    if request.method == 'POST':
        old_pic_filename = category.category_picture

        new_name = request.form['category_name']
        same_category_name_exists = Category.query.filter_by(category_name=new_name).first() if new_name != category.category_name else None

        new_image = request.files['category_picture']
        pic_filename = secure_filename(new_image.filename) 

        
        if category is None:
            flash('Category does not exist.', category='error')
            return redirect(url_for('auth_admin.category_list'))
        

        if same_category_name_exists:
            flash('There is another category with the same name.', category='error')
            return redirect(url_for('auth_admin.edit_category', category_id=category_id))
        

        elif len(new_name) < 3 or len(new_name) > 40 or new_name == category.category_name:
            if pic_filename != '' and 'category_picture' in request.files and allowed_file(pic_filename):
                try:
                    db.session.begin_nested()
                    # Delete old picture
                    delete_picture(old_pic_filename)
                    
                    # Save new picture
                    new_pic_filename = save_picture(new_image, pic_filename)
                    category.category_picture = new_pic_filename

                    db.session.commit()

                    flash('Category image updated!', category='success')
                    flash('Check category name.', category='error')
                    return redirect(url_for('auth_admin.view_category', category_id=category_id))
                
                except IntegrityError:
                    db.session.rollback()
                    flash('Something went wrong.', category='error')
                    return redirect(url_for('auth_admin.edit_category', category_id=category_id))
                
                finally:
                    db.session.close()
            
            else:
                flash('Check category details.', category='error')
                return redirect(url_for('auth_admin.edit_category', category_id=category_id))
        

        elif new_name != category.category_name and len(new_name) >= 3 and len(new_name) <= 40:
            if pic_filename != '' and 'category_picture' in request.files and allowed_file(pic_filename):
                try:
                    db.session.begin_nested()

                    # Update category name
                    category.category_name = new_name
                    
                    # Delete old picture
                    delete_picture(old_pic_filename)
                    
                    # Save new picture
                    new_pic_filename = save_picture(new_image, pic_filename)
                    category.category_picture = new_pic_filename
                    
                    db.session.commit()

                    flash('Category updated!', category='success')
                    return redirect(url_for('auth_admin.view_category', category_id=category_id))
                
                except IntegrityError:
                    db.session.rollback()
                    flash('Something went wrong.', category='error')
                    return redirect(url_for('auth_admin.edit_category', category_id=category_id))
                
                finally:
                    db.session.close()
            
            else:
                try:
                    db.session.begin_nested()

                    # Update category name
                    category.category_name = new_name
                    
                    db.session.commit()

                    flash('Category updated!', category='success')
                    return redirect(url_for('auth_admin.view_category', category_id=category_id))
                
                except IntegrityError:
                    db.session.rollback()
                    flash('Something went wrong.', category='error')
                    return redirect(url_for('auth_admin.edit_category', category_id=category_id))
                
                finally:
                    db.session.close()
        
        
        else:
            flash('Something went wrong.', category='error')
            return redirect(url_for('auth_admin.edit_category', category_id=category_id))

    
    return render_template('admin/category_pages/edit_category.html', category=category, user=current_user, category_id=category_id)

@auth_admin.route('/delete_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id) # Use query.get() depending on the situation
    
    if request.method == 'POST':
        try:
            db.session.begin_nested()

            # Find all products in that category and delete them
            products = Product.query.filter_by(category_id=category_id).all()
            
            if products:
                for product in products:
                    # Delete product picture
                    prod_pic_filename = product.product_picture
                    delete_picture(prod_pic_filename)

                    db.session.delete(product)

                # Delete category picture
                pic_filename = category.category_picture
                delete_picture(pic_filename)
                
                db.session.delete(category)
                db.session.commit()

                flash(f'Category "{category.category_name}" has been deleted.', 'success')
                return redirect(url_for('auth_admin.category_list'))
            
            else:
                # Delete category picture
                pic_filename = category.category_picture
                delete_picture(pic_filename)
                
                db.session.delete(category)
                db.session.commit()
                flash(f'Category "{category.category_name}" has been deleted.', 'success')
                return redirect(url_for('auth_admin.category_list'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Something went wrong.', category='error')
            return redirect(url_for('auth_admin.category_list'))
        
        finally:
            db.session.close()

    return render_template('admin/category_pages/delete_category.html', category=category, user=current_user)
    


############################################################################################################################
'''
--------------------------------  CRUD FOR PRODUCT  --------------------------------
'''
############################################################################################################################


# Create new product
@auth_admin.route('/new_product', methods=['GET', 'POST'])
@login_required
def new_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product = Product.query.filter_by(product_name=product_name).first()


        if 'product_picture' not in request.files:
            flash('Upload an image.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        product_picture = request.files['product_picture']
        pic_filename = secure_filename(product_picture.filename)


        total_quantity = int(request.form.get('total_quantity'))
        rate_per_unit = int(request.form.get('rate_per_unit'))
        manufacture_date_str = request.form['manufacture_date']
        manufacture_date = datetime.strptime(manufacture_date_str, '%Y-%m-%d').date()
        unit_id = int(request.form.get('unit_id'))
        category_id = int(request.form.get('category_id'))


        if product:
            flash('Product already exists.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        

        # Product name is checked below
        elif len(product_name) < 3:
            flash('Product name must be greater than 2 characters.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif len(product_name) > 40:
            flash('Product name must be less than 40 characters.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        

        # Product picture is checked below
        elif pic_filename == '':
            flash('No selected file.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif not allowed_file(pic_filename):
            flash('File type must be svg, webp, png, jpg or jpeg.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        

        # Manufacture date is checked below
        elif manufacture_date == '' or manufacture_date == None:
            flash('Manufacture date cannot be empty.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif manufacture_date > datetime.now().date():
            flash('Manufacture date cannot be greater than today.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        

        # Total quantity is checked below
        elif total_quantity == '' or total_quantity == None:
            flash('Total quantity cannot be empty.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif total_quantity < 0:
            flash('Total quantity cannot be negative.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif total_quantity > 1000000:
            flash('Total quantity cannot be greater than 1000000.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        
        # Rate per unit is checked below
        elif rate_per_unit == '' or rate_per_unit == None:
            flash('Rate per unit cannot be empty.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif rate_per_unit < 0:
            flash('Rate per unit cannot be negative.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif rate_per_unit > 100000:
            flash('Rate per unit cannot be greater than 100000.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        

        # Unit and category IDs are checked below
        elif unit_id == '' or unit_id == None:
            flash('Select a unit.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif category_id == '' or category_id == None:
            flash('Select a category.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif unit_id <= 0:
            flash('Select a unit.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        elif category_id <= 0:
            flash('Select a category.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
        
        # Create new product
        elif pic_filename and product_picture and allowed_file(pic_filename) and product_name and total_quantity and rate_per_unit and manufacture_date and unit_id and category_id:
            try:
                db.session.begin_nested()

                new_product = Product(product_name=product_name, total_quantity=total_quantity, rate_per_unit=rate_per_unit, manufacture_date=manufacture_date, unit_id=unit_id, category_id=category_id)
                new_pic_filename = save_picture(product_picture, pic_filename)
                new_product.product_picture = new_pic_filename

                db.session.add(new_product)
                db.session.commit()

                flash('Product created!', category='success')
                new_prod = Product.query.filter_by(product_name=product_name).first()
                return redirect(url_for('auth_admin.view_product', product_id=new_prod.id))
            
            except IntegrityError:
                db.session.rollback()
                flash('Something went wrong.', category='error')
                return redirect(url_for('auth_admin.new_product'))
            
            finally:
                db.session.close()
        

        else:
            flash('Something went wrong.', category='error')
            return redirect(url_for('auth_admin.new_product'))
        
    units = Unit.query.all()
    categories = Category.query.all()
    return render_template('admin/product_pages/new_product.html', user=current_user, categories=categories, units=units)
    
# Read product
@auth_admin.route('/view_product/<int:product_id>')
@login_required
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('admin/product_pages/view_product.html', user=current_user, product=product, product_id=product_id)

# Update product
@auth_admin.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get(product_id)

    if request.method == 'POST':
        old_pic_filename = product.product_picture

        new_name = request.form['product_name']
        same_prod_name_exists = Product.query.filter_by(product_name=new_name).first() if new_name != product.product_name else None

        new_image = request.files['product_picture']
        pic_filename = secure_filename(new_image.filename)

        new_total_quantity = int(request.form.get('total_quantity'))
        new_rate_per_unit = int(request.form.get('rate_per_unit'))
        new_manufacture_date_str = request.form['manufacture_date']
        new_manufacture_date = datetime.strptime(new_manufacture_date_str, '%Y-%m-%d').date()
        new_unit_id = int(request.form.get('unit_id'))
        new_category_id = int(request.form.get('category_id'))

        
        def empty_data_or_out_of_range():
            bool_flag = False
            
            if len(new_name)<3 or len(new_name)>40 \
            or new_manufacture_date=='' or new_manufacture_date==None or new_manufacture_date > datetime.now().date() \
            or new_total_quantity=='' or new_total_quantity==None or new_total_quantity < 0 or new_total_quantity > 1000000 \
            or new_rate_per_unit=='' or new_rate_per_unit==None or new_rate_per_unit < 0 or new_rate_per_unit > 100000 \
            or new_unit_id=='' or new_unit_id==None or new_unit_id <= 0 or new_category_id=='' \
            or new_category_id==None or new_category_id <= 0:
                bool_flag = True
                return bool_flag
            
            return bool_flag
        
        def no_data_changed():
            bool_flag = False

            if new_name==product.product_name and new_manufacture_date==product.manufacture_date \
            and new_total_quantity==product.total_quantity and new_rate_per_unit==product.rate_per_unit \
            and new_unit_id==product.unit_id and new_category_id==product.category_id:
                bool_flag = True
                return bool_flag
            
            return bool_flag
                

        if product is None:
            flash('Product does not exist.', category='error')
            return redirect(url_for('auth_admin.product_list'))


        elif same_prod_name_exists:
            flash('There is another product with the same name.', category='error')
            return redirect(url_for('auth_admin.edit_product', product_id=product_id))
        

        elif pic_filename != '' and 'product_picture' in request.files and allowed_file(pic_filename):
            if empty_data_or_out_of_range() or no_data_changed():
                try:
                    db.session.begin_nested()

                    # Delete old picture and save new picture
                    delete_picture(old_pic_filename)
                    new_pic_filename = save_picture(new_image, pic_filename)
                    product.product_picture = new_pic_filename

                    db.session.commit()

                    flash('Product image updated!', category='success')
                    return redirect(url_for('auth_admin.view_product', product_id=product_id))
                
                except IntegrityError:
                    db.session.rollback()
                    flash('Something went wrong.', category='error')
                    return redirect(url_for('auth_admin.edit_product', product_id=product_id))
                
                finally:
                    db.session.close()
            
            else:
                try:
                    db.session.begin_nested()
                    
                    # Delete old picture and save new picture
                    delete_picture(old_pic_filename)
                    new_pic_filename = save_picture(new_image, pic_filename)
                    product.product_picture = new_pic_filename
                    
                    # Update other data
                    product.product_name = new_name
                    product.total_quantity = new_total_quantity
                    product.rate_per_unit = new_rate_per_unit
                    product.manufacture_date = new_manufacture_date
                    product.unit_id = new_unit_id
                    product.category_id = new_category_id
                    
                    db.session.commit()

                    flash('Product updated!', category='success')
                    return redirect(url_for('auth_admin.view_product', product_id=product_id))
                
                except IntegrityError:
                    db.session.rollback()
                    flash('Something went wrong.', category='error')
                    return redirect(url_for('auth_admin.edit_product', product_id=product_id))
                
                finally:
                    db.session.close()
        

        elif empty_data_or_out_of_range():
            flash('Enter valid data.', category='error')
            return redirect(url_for('auth_admin.edit_product', product_id=product_id))
        

        elif no_data_changed():
            flash('Enter new data.', category='error')
            return redirect(url_for('auth_admin.edit_product', product_id=product_id))


        else:
            try:
                db.session.begin_nested()
                
                product.product_name = new_name
                product.total_quantity = new_total_quantity
                product.rate_per_unit = new_rate_per_unit
                product.manufacture_date = new_manufacture_date
                product.unit_id = new_unit_id
                product.category_id = new_category_id
                
                db.session.commit()

                flash('Product updated!', category='success')
                return redirect(url_for('auth_admin.view_product', product_id=product_id))
            
            except IntegrityError:
                db.session.rollback()
                flash('Something went wrong.', category='error')
                return redirect(url_for('auth_admin.edit_product', product_id=product_id))
            
            finally:
                db.session.close()
    

    units = Unit.query.all()
    categories = Category.query.all()
    return render_template('admin/product_pages/edit_product.html', product=product, user=current_user, product_id=product_id, units=units, categories=categories)

# Delete product
@auth_admin.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        try:
            db.session.begin_nested()
            # Delete product picture
            pic_filename = product.product_picture
            delete_picture(pic_filename)
            
            db.session.delete(product)
            db.session.commit()

            flash(f'Product "{product.product_name}" has been deleted.', 'success')
            return redirect(url_for('auth_admin.product_list'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Something went wrong.', category='error')
            return redirect(url_for('auth_admin.product_list'))
        
        finally:
            db.session.close()

    return render_template('admin/product_pages/delete_product.html', product=product, user=current_user, product_id=product_id)



############################################################################################################################
'''
--------------------------------  CRUD FOR UNIT  --------------------------------
'''
############################################################################################################################


# Create new unit
@auth_admin.route('/new_unit', methods=['GET', 'POST'])
@login_required
def new_unit():
    if request.method == 'POST':
        unit_name = request.form.get('unit_name')
        unit = Unit.query.filter_by(unit_name=unit_name).first()

        if unit:
            flash('Unit already exists.', category='error')
        
        elif len(unit_name) < 2:
            flash('Unit must be greater than 1 character.', category='error')
        
        else:
            try:
                db.session.begin_nested()

                new_unit = Unit(unit_name=unit_name)

                db.session.add(new_unit)
                db.session.commit()

                flash('Unit created!', category='success')
                return render_template('admin/unit_pages/new_unit.html', user=current_user)
            
            except IntegrityError:
                db.session.rollback()
                flash('Something went wrong.', category='error')
                return redirect(url_for('auth_admin.new_unit'))
            
            finally:
                db.session.close()
        
        return redirect(url_for('views.admin_view'))
    
    return render_template('admin/unit_pages/new_unit.html', user=current_user)

# Read unit
@auth_admin.route('/view_unit/<int:unit_id>')
@login_required
def view_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    return render_template('admin/unit_pages/view_unit.html', user=current_user, unit=unit, unit_id=unit_id)

# Update unit
@auth_admin.route('/edit_unit/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def edit_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)

    if request.method == 'POST':
        new_name = request.form['unit_name']
        new_name_check = Unit.query.filter_by(unit_name=new_name).first() if new_name != unit.unit_name else None
        
        if len(new_name) < 2:
            flash('Unit must be greater than 1 character.', category='error')
            return redirect(url_for('auth_admin.edit_unit', unit_id=unit_id))
        
        elif new_name_check:
            flash('Unit already exists.', category='error')
            return redirect(url_for('auth_admin.edit_unit', unit_id=unit_id))
        
        elif new_name == unit.unit_name:
            flash('Input is same as the old data.', category='error')
            return redirect(url_for('auth_admin.edit_unit', unit_id=unit_id))
        
        else:
            try:
                db.session.begin_nested()

                unit.unit_name = new_name
                db.session.commit()

                flash('Unit updated!', category='success')
                return redirect(url_for('auth_admin.view_unit', unit_id=unit_id))
            
            except IntegrityError:
                db.session.rollback()
                flash('Something went wrong.', category='error')
                return redirect(url_for('auth_admin.edit_unit', unit_id=unit_id))
            
            finally:
                db.session.close()

    return render_template('admin/unit_pages/edit_unit.html', unit=unit, user=current_user, unit_id=unit_id)

# Delete unit
@auth_admin.route('/delete_unit/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def delete_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)

    if request.method == 'POST':
        try:
            db.session.begin_nested()

            db.session.delete(unit)
            db.session.commit()

            flash(f'Unit "{unit.unit_name}" has been deleted.', 'success')
            return redirect(url_for('auth_admin.unit_list'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Something went wrong.', category='error')
            return redirect(url_for('auth_admin.unit_list'))
        
        finally:
            db.session.close()
    
    return render_template('admin/unit_pages/delete_unit.html', unit=unit, user=current_user, unit_id=unit_id)

