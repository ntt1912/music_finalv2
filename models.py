from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # ... Define other methods and relationships for the User model ...


class Tracks(db.Model):
    id_track = db.Column(db.String(length=50), primary_key=True)
    title = db.Column(db.String(length=50), nullable=True)
    img = db.Column(db.String(length=200))

    # ... Define other methods and relationships for the Tracks model ...


class Albums(db.Model):
    id = db.Column(db.String(length=50), primary_key=True)
    title = db.Column(db.String(length=50), nullable=True)
    image = db.Column(db.String(length=200))

    # ... Define other methods and relationships for the Albums model ...


class Playlist(db.Model):
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)
    id_track = db.Column(
        db.Integer(), db.ForeignKey("tracks.id_track"), primary_key=True
    )
    user = db.relationship("User", backref="tracks", lazy=True)
    tracks = db.relationship("Tracks", backref="user", lazy=True)

    # ... Define other methods and relationships for the Playlist model ...


class TBA(db.Model):
    album_id = db.Column(db.Integer, db.ForeignKey("albums.id"), primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id_track"), primary_key=True)
    position = db.Column(db.Integer)
    album = db.relationship("Albums", backref="tracks", lazy=True)
    track = db.relationship("Tracks", backref="album", lazy=True)

    # ... Define other methods and relationships for the TBA model ...
