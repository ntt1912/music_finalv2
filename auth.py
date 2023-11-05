from flask import Blueprint,render_template,flash,redirect,url_for
from flask_mail import Message
from app import app, mail  # Import your Flask app and mail instance
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask_login import login_user, logout_user, current_user
from models import User  # Import your User model
from .forms import RegisterForm, LoginForm, ResetRequestForm, ResetPasswordForm
from flask_login import login_user

auth = Blueprint("auth", __name__)

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
        return redirect(url_for("login_page"))
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