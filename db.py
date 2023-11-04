from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_login import UserMixin
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from flask_admin import Admin
from flask import abort
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SECRET_KEY'] = '3e7b5ec2a82b029ad8500095'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'ChienNV.B20VT063@stu.ptit.edu.vn'
app.config['MAIL_PASSWORD'] = 'C11122002'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer(),primary_key = True)
    username = db.Column(db.String(length=30),nullable = False,unique = True)
    email_address = db.Column(db.String(length=50),nullable = False,unique = True)
    password_hash = db.Column(db.String(length=50),nullable = False)
    is_admin = db.Column(db.Boolean,default = False)
    def __repr__(self) -> str:
        return f'<User> {self.username}'

    def get_token(self,expires_sec=300):
        serial = Serializer(app.config['SECRET_KEY'])
        return serial.dumps({'user_id':self.id})
    
    @staticmethod
    def verify_token(token):
        serial = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    @property
    def password(self):
        return self.password_hash
    @password.setter
    def password(self,plan_text_passeword):
        self.password_hash = bcrypt.generate_password_hash(plan_text_passeword,10).decode('utf-8')

    def check_password_correction(self, attempted_password):
        if bcrypt.check_password_hash(self.password_hash, attempted_password):
            return True
        return False

class Tracks(db.Model):
    id_track = db.Column(db.String(length=50),primary_key =True)
    title = db.Column(db.String(length=50),nullable = True)
    img = db.Column(db.String(length = 200))

class Albums(db.Model):
    id = db.Column(db.String(length=50),primary_key =True)
    title = db.Column(db.String(length=50),nullable = True)
    image = db.Column(db.String(length = 200))


class Playlist(db.Model):
    user_id = db.Column(db.Integer(),db.ForeignKey('user.id'),primary_key = True)
    id_track = db.Column(db.Integer(),db.ForeignKey('tracks.id_track'),primary_key  = True)
    user = db.relationship('User',backref = "tracks",lazy = True)
    tracks = db.relationship('Tracks',backref='user',lazy = True)


admin = Admin(app,template_mode='bootstrap3')


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
    form_columns = [
        'user_id',
        'song_id',
    ]
    list_columns = [
        'user_id',
        'song_id',
    ]

admin.add_view(UserView(User,db.session))
admin.add_view(ModelView(Tracks,db.session))
admin.add_view(ModelView(Playlist,db.session))
admin.add_view(ModelView(Albums,db.session))

app.run(debug=True)