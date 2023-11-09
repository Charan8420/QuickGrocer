from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from . import db

bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(160), unique=False, nullable=False)

    # One to many relationship with Cart
    cart = db.relationship('Cart', backref='user')


    # Functions
    def __repr__(self):
        return '<User %r>' % self.username
    
    ''' Functions for user password '''
    @property
    def password(self):
        return self.password_hash
    
    @password.setter
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    ''' Set user.is_admin to False(for navbar) '''
    def is_admin(self):
        return False


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # One user can have many cart objects each with different product_id
    prod_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)


    # Functions
    def __repr__(self):
        return '<Cart %r>' % self.id


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(80), unique=True, nullable=False)
    product_picture = db.Column(db.String(160), nullable=False, default='default.png')
    total_quantity = db.Column(db.Integer, unique=False, nullable=False)
    rate_per_unit = db.Column(db.Integer, unique=False, nullable=False)
    manufacture_date = db.Column(db.Date, unique=False, nullable=False)
    
    # Foreign keys
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    # One to many relationship with Cart
    cart = db.relationship('Cart', backref='product', lazy=True)


    #   Functions
    def __repr__(self):
        return '<Product %r>' % self.product_name


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(80), unique=True, nullable=False)
    category_picture = db.Column(db.String(80), nullable=False, default='default.png')
    products = db.relationship('Product', backref='category', lazy=True)


    # Functions
    def __repr__(self):
        return '<Category %r>' % self.category_name


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(160), unique=False, nullable=False)


    # Functions
    def __repr__(self):
        return '<Admin %r>' % self.admin_name
    ''' Functions for admin password '''
    @property
    def password(self):
        return self.password_hash
    
    @password.setter
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    ''' Set user.is_admin to True(for navbar) '''
    def is_admin(self):
        return True


class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship('Product', backref='unit', lazy=True)


    # Functions
    def __repr__(self):
        return '<Unit %r>' % self.unit_name




        