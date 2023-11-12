from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from website.models import User


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
