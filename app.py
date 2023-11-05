from flask import Flask,g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from admin import admin
import sqlite3
from routes import routes
from auth import auth
app = Flask(__name__)

# Configuration settings for your Flask app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music.db"
app.config["SECRET_KEY"] = "3e7b5ec2a82b029ad8500095"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy, Bcrypt, LoginManager, and Mail with the app
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
admin = Admin(app, template_mode="bootstrap3")
app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(routes, url_prefix="/")

# Configure Flask-Login settings
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

# Configure Mail settings
app.config["MAIL_SERVER"] = "smtp.office365.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "ChienNV.B20VT063@stu.ptit.edu.vn"
app.config["MAIL_PASSWORD"] = "C11122002"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False


def connect_db():
    sql = sqlite3.connect("instance/music.db")  # Use forward slash instead of backslash
    sql.row_factory = sqlite3.Row  # Return results as dictionaries instead of tuples
    return sql


def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True)
