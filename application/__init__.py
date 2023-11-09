from flask import Flask, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user


db = SQLAlchemy()
DB_NAME = "database.sqlite3"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "JyHUS*(67679*^&3!$jiJS*Hs" 
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    
    from .views import views
    from .auth_user import auth_user
    from .auth_admin import auth_admin
    from .models import User, Admin, Cart, Product, Category, Unit
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth_user, url_prefix="/")
    app.register_blueprint(auth_admin, url_prefix="/admin")
    
    create_database(app)

    login_manager = LoginManager(app)
    login_manager.blueprint_login_views = {'auth_user': 'auth_user.login', 'auth_admin': 'auth_admin.admin_login'}
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        if session.get('user_type') == 'admin':
            x = Admin.query.get(str(id))
        elif session.get('user_type') == 'user':
            x = User.query.get(str(id))
        else:
            x = None  
        return x
    
    return app


def create_database(app):
    from .models import User, Admin, Cart, Product, Category, Unit
    if not path.exists("application/" + DB_NAME):
        with app.app_context():
            db.create_all()
            
        print("Created database!")





