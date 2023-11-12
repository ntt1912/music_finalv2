from website import get_db, db, app
from website.models import Tracks, Playlist, Albums
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from flask_login import login_required
import random


@app.route("/")
def home_page():
    return render_template("home.html")


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
@login_required
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
