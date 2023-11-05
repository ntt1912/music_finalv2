from flask import Flask,g, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_login import UserMixin
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask_admin import Admin
from flask import abort
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError

from flask_login import login_user, logout_user, login_required
from flask_mail import Message

import random
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
    sql = sqlite3.connect('instance\music.db')
    sql.row_factory = sqlite3.Row #tra ve dictionary thay vi tuple
    return sql 

def get_db():
    if not hasattr(g,'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User> {self.username}"

    def get_token(self, expires_sec=300):
        serial = Serializer(app.config["SECRET_KEY"])
        return serial.dumps({"user_id": self.id})

    @staticmethod
    def verify_token(token):
        serial = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = serial.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, plan_text_passeword):
        self.password_hash = bcrypt.generate_password_hash(
            plan_text_passeword, 10
        ).decode("utf-8")

    def check_password_correction(self, attempted_password):
        if bcrypt.check_password_hash(self.password_hash, attempted_password):
            return True
        return False


class Tracks(db.Model):
    id_track = db.Column(db.String(length=50), primary_key=True)
    title = db.Column(db.String(length=50), nullable=True)
    img = db.Column(db.String(length=200))


class Albums(db.Model):
    id = db.Column(db.String(length=50), primary_key=True)
    title = db.Column(db.String(length=50), nullable=True)
    image = db.Column(db.String(length=200))


class Playlist(db.Model):
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)
    id_track = db.Column(
        db.Integer(), db.ForeignKey("tracks.id_track"), primary_key=True
    )
    user = db.relationship("User", backref="tracks", lazy=True)
    tracks = db.relationship("Tracks", backref="user", lazy=True)


admin = Admin(app, template_mode="bootstrap3")


class Admin_Controll(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        else:
            return abort(404)


class UserView(ModelView):
    def on_model_change(self, form, model, is_created):
        model.password_hash = bcrypt.generate_password_hash(model.password_hash)


class PlaylistView(Admin_Controll):
    list_columns = [
        "user_id",
        "id_track",
    ]


class TrackView(Admin_Controll):
    list_columns = ["id_track", "title", "img"]


admin.add_view(UserView(User, db.session))
admin.add_view(TrackView(Tracks, db.session))
admin.add_view(PlaylistView(Playlist, db.session))
admin.add_view(ModelView(Albums, db.session))


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("Username already exits! Please try another username")

    def validate_email_address(self, email_to_check):
        email = User.query.filter_by(email_address=email_to_check.data).first()
        if email:
            raise ValidationError("Email already exits! Please try another Email")

    username = StringField(
        label="User Name:", validators=[Length(min=2, max=30), DataRequired()]
    )
    email_address = StringField(
        label="EMAIL ADDRESS:", validators=[Email(), DataRequired()]
    )
    password1 = PasswordField(
        label="ENTER YOUR PASSWORD:", validators=[Length(min=6), DataRequired()]
    )
    password2 = PasswordField(
        label="VERIFY:", validators=[EqualTo("password1"), DataRequired()]
    )
    submit = SubmitField(label="Create ACCOUNT")


class LoginForm(FlaskForm):
    username = StringField(label="User Name ", validators=[DataRequired()])
    password = PasswordField(label="PassWord ", validators=[DataRequired()])
    submit = SubmitField(label="Sign in")


class ResetRequestForm(FlaskForm):
    email_address = StringField(label="Email Address", validators=[DataRequired()])
    submit = SubmitField(label="Reset Password")


class ResetPasswordForm(FlaskForm):
    password1 = PasswordField(
        label="ENTER YOUR PASSWORD:", validators=[Length(min=6), DataRequired()]
    )
    password2 = PasswordField(
        label="VERIFY:", validators=[EqualTo("password1"), DataRequired()]
    )
    submit = SubmitField(label="ChangePassword")


@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data,
        )
        db.session.add(user_to_create)
        db.session.commit()
        flash("You just created successfully", category="success")
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(
                f"There was an error with creating a user: {err_msg}", category="danger"
            )
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            if attempted_user.username == "admin":
                return redirect("/admin")
            flash(
                f"Success! You just logged in as {attempted_user.username}",
                category="success",
            )
            return redirect(url_for("getsongs"))
        else:
            flash(
                "Username and password are not match! Please try again",
                category="danger",
            )
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    flash("You have been loged out", category="success")
    return redirect(url_for("home_page"))


def send_mail(user):
    token = user.get_token()
    msg = Message(
        "Password Reset Request",
        recipients=[user.email_address],
        sender="ChienNV.B20VT063@stu.ptit.edu.vn",
    )
    msg.body = f""" to reset your password. Please follow the link below

    {url_for('reset_token',token = token,_external = True)}

    If you didn't send a password reset request. Please ignore this message.

 """
    mail.send(msg)


@app.route("/reset_password", methods=["POST", "GET"])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user:
            send_mail(user)
            flash("Reset request sent. Check your mail")
            return redirect(url_for("login_page"))
        else:
            flash("Email is not exist")
    return render_template("reset_request.html", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash("That is invalid token or expired.Please try again")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password1.data).decode(
            "utf-8"
        )
        user.password_hash = hash_password
        db.session.commit()
        flash("Password changed!")
        return redirect(url_for("login_page"))
    return render_template("changepass.html", form=form)


@app.route("/changepassword", methods=["GET", "POST"])
def changepass():
    pass


@app.route("/getsongs", methods=["GET"])
@login_required
def getsongs():
    songs = random.sample(Tracks.query.all(), 5)
    return render_template("home.html", songs=songs)


@app.route("/addtopl", methods=["GET", "POST"])
def addtopl():
    if request.method == "POST":
        song_id = request.form["song_id"]
        user_id = current_user.get_id()

        usersong = Playlist(user_id=user_id, id_track=song_id)
        db.session.add(usersong)
        db.session.commit()
        flash("Successfully", category="success")
    return render_template("home.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_query = request.form["search_query"]
        # Thực hiện tìm kiếm trong cơ sở dữ liệu theo query
        search_results = Tracks.query.filter(
            Tracks.title.like(f"%{search_query}%")
        ).all()
        return render_template("search.html", search_results=search_results)
    return render_template("search.html")


@app.route("/play_song/<song_id>")
def play_song(song_id):
    song = Tracks.query.filter_by(id_track=song_id).first()
    return render_template("play_song.html", song=song)


@app.route("/add_to_playlist/<song_id>")
@login_required
def add_to_playlist(song_id):
    user_id = current_user.get_id()
    usersong = Playlist(user_id=user_id, id_track=song_id)
    db.session.add(usersong)
    db.session.commit()
    flash("Successfully", category="success")
    return redirect(url_for("search"))


@app.route("/search_album", methods=["GET", "POST"])
def search_album():
    if request.method == "POST":
        search_query = request.form["search_query"]
        albums = Albums.query.filter(Albums.title.like(f"%{search_query}%")).all()
        return render_template("search_album.html", albums=albums)

    return render_template("search_album.html")

@app.route("/showplaylist",methods = ['GET'])
def show_playlist():
    user_id = current_user.get_id()
    dbm = get_db()
    cur = dbm.execute(
        ''' 
            select tracks.id_track
            from user
            left outer join playlist
            on playlist.user_id = user.id
            left outer join tracks
            on tracks.id_track = playlist.id_track 
            where user.id = ?

        ''',[user_id]
        )
    songs_result = cur.fetchall()
    return render_template('showplaylist.html',songs = songs_result)

@app.route("/tophit",methods = ['GET'])
def tophit():
    dbm = get_db()
    cur = dbm.execute(
        ''' 
            select
            id_track, 
            count(*)
            from playlist
            group by id_track
            order by count(*) desc
            limit(10)

        '''
        )
    songs_result = cur.fetchall()
    return render_template('tophit.html',songs = songs_result)


if __name__ == "__main__":
    app.run(debug=True)