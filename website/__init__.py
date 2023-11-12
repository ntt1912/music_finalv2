from flask import Flask,g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import sqlite3

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music.db"
app.config["SECRET_KEY"] = "3e7b5ec2a82b029ad8500095"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.app_context().push()


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

app.config["MAIL_SERVER"] = "smtp.office365.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "ChienNV.B20VT063@stu.ptit.edu.vn"
app.config["MAIL_PASSWORD"] = "C11122002"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False


mail = Mail(app)

def connect_db():
    sql = sqlite3.connect("instance\\music.db")
    sql.row_factory = sqlite3.Row  # tra ve dictionary thay vi tuple
    return sql


def get_db():
    if not hasattr(g, "sqlite3"):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


from website import auth
from website import admin
from website import views