from website import db,app
from flask_login import UserMixin
from website import bcrypt
from website import login_manager
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

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

    def __repr__(self) -> str:
        return self.username


class Tracks(db.Model):
    id_track = db.Column(db.String(length=50), primary_key=True)
    title = db.Column(db.String(length=50), nullable=True)
    img = db.Column(db.String(length=200))

    def __repr__(self) -> str:
        return self.id_track


class Albums(db.Model):
    id = db.Column(db.String(length=50), primary_key=True)
    title = db.Column(db.String(length=50), nullable=True)
    image = db.Column(db.String(length=200))

    def __repr__(self) -> str:
        return self.id


class Playlist(db.Model):
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)
    id_track = db.Column(
        db.Integer(), db.ForeignKey("tracks.id_track"), primary_key=True
    )
    user = db.relationship("User", backref="tracks", lazy=True)
    tracks = db.relationship("Tracks", backref="user", lazy=True)


class TBA(db.Model):
    album_id = db.Column(db.Integer, db.ForeignKey("albums.id"), primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id_track"), primary_key=True)
    position = db.Column(db.Integer)
    album = db.relationship("Albums", backref="tracks", lazy=True)
    track = db.relationship("Tracks", backref="album", lazy=True)