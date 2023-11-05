from flask import render_template,flash,redirect,url_for,request,Blueprint,
from flask_login import login_required, current_user
from app import app, db  # Import your Flask app and SQLAlchemy instance
from .models import Tracks, Playlist, Albums  # Import your models

routes = Blueprint("routes", __name__)

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


@app.route("/getsongs", methods=["GET"])
@login_required
def getsongs():
    songs = random.sample(Tracks.query.all(), 200)
    return render_template("Songs.html", songs=songs)


@app.route("/addtopl", methods=["GET", "POST"])
def addtopl():
    dbm = get_db()
    if request.method == "POST":
        song_id = request.form["song_id"]
        user_id = current_user.get_id()
        existing_entry = Playlist.query.filter_by(
            user_id=user_id, id_track=song_id
        ).first()
        if existing_entry:
            flash("Song is already in your playlist.", category="info")
        else:
            usersong = Playlist(user_id=user_id, id_track=song_id)
            db.session.add(usersong)
            db.session.commit()
            flash("Added to playlist successfully", category="success")
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
    existing_entry = Playlist.query.filter_by(user_id=user_id, id_track=song_id).first()
    if existing_entry:
        flash("Song is already in your playlist.", category="info")
    else:
        usersong = Playlist(user_id=user_id, id_track=song_id)
        db.session.add(usersong)
        db.session.commit()
        flash("Added to playlist successfully", category="success")
    return redirect(url_for("getsongs"))


@app.route("/search_album", methods=["GET", "POST"])
def search_album():
    if request.method == "POST":
        search_query = request.form["search_query"]
        albums = Albums.query.filter(Albums.title.like(f"%{search_query}%")).all()
        return render_template("search_album.html", albums=albums)

    return render_template("search_album.html")


@app.route("/showplaylist", methods=["GET"])
def show_playlist():
    user_id = current_user.get_id()
    dbm = get_db()
    cur = dbm.execute(
        """ 
            select tracks.id_track
            from user
            left outer join playlist
            on playlist.user_id = user.id
            left outer join tracks
            on tracks.id_track = playlist.id_track 
            where user.id = ?

        """,
        [user_id],
    )
    songs_result = cur.fetchall()
    return render_template("showplaylist.html", songs=songs_result)


@app.route("/tophit", methods=["GET"])
def tophit():
    dbm = get_db()
    cur = dbm.execute(
        """ 
            select
            id_track, 
            count(*)
            from playlist
            group by id_track
            order by count(*) desc
            limit(10)

        """
    )
    songs_result = cur.fetchall()
    return render_template("tophit.html", songs=songs_result)


@app.route("/viewalbum/<string:album_id>", methods=["GET"])
def viewalbum(album_id):
    dbm = get_db()
    cur = dbm.execute(
        """
        select track_id
        from tba
        where album_id = ?
         """,
        [album_id],
    )
    result = cur.fetchall()
    cur = dbm.execute(
        """
        select title
        from albums
        where id = ?
        """,
        [album_id],
    )
    album_name = cur.fetchone()
    return render_template("album.html", songs=result, album_name=album_name)


@app.route("/remove_from_playlist/<song_id>", methods=["GET"])
@login_required
def remove_from_playlist(song_id):
    user_id = current_user.get_id()
    playlist_entry = Playlist.query.filter_by(user_id=user_id, id_track=song_id).first()
    if playlist_entry:
        db.session.delete(playlist_entry)
        db.session.commit()
        flash("Removed from playlist successfully", category="success")
    return redirect(url_for("show_playlist"))