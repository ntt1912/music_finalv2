from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import abort
from flask_login import current_user
from app import app, db, bcrypt
from models import User, Tracks, Playlist, Albums, TBA


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
    column_list = [
        "user_id",
        "id_track",
    ]
    form_choices = {
        "user": [("user_id", User.query.all())],
        "tracks": [("id_track", Tracks.query.all())],
    }


class TrackView(Admin_Controll):
    column_list = ["id_track", "title", "img"]


class TBAView(Admin_Controll):
    column_list = ["album_id", "track_id", "position"]


admin = Admin(app, template_mode="bootstrap3")
admin.add_view(UserView(User, db.session))
admin.add_view(TrackView(Tracks, db.session))
admin.add_view(PlaylistView(Playlist, db.session))
admin.add_view(ModelView(Albums, db.session))
admin.add_view(TBAView(TBA, db.session))
