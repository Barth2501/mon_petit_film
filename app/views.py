from flask import render_template, redirect, url_for, Flask, request, session, flash
from flask_pymongo import PyMongo
from app.classes.user import User
from app.classes.ratings import Ratings
from app.classes.movies_and_series import Movie, TVShow
from app.svd import recommend_movies
import random
from flask_mail import Mail
import app.config as config


app = Flask(__name__)
app.config.from_object(config)

mail = Mail(app)

mongo = PyMongo(app)

genres_db = mongo.db.genres
genres_tvshow_db = mongo.db.genres_tvshow

### GET ROUTES (PAGES)

# Home
@app.route("/")
def home():
    return redirect(url_for("index"))


@app.route("/index")
def index():
    return render_template("index.html")


# First ratings after signup
@app.route("/first_ratings", methods=["GET"])
def first_ratings():
    movies = Movie.filter(vote_count={"$gt": 2000})
    film_sample = []
    poster_sample = []
    id_sample = []
    while len(film_sample) < 10:
        film = movies[random.randint(1, len(movies))].json
        film.pop("ratings")
        film_sample.append(film)
        poster_sample.append(film["poster_path"])
        id_sample.append(film["id"])
    return render_template(
        "first_ratings.html",
        film_sample=film_sample,
        poster_sample=poster_sample,
        id_sample=id_sample,
    )


# Movies pages
@app.route("/movies", methods=["GET"])
def movies():
    # from app.celery import hello
    # hello.delay()
    if "username" not in session or "id" not in session:
        return redirect(url_for("index"))
    reco_movies = recommend_movies(session["id"], 80)[1]
    dict_reco_movies = reco_movies.to_dict("records")
    genres_list = []
    movies_by_genre = {}
    for genre in genres_db.find():
        genre.pop("_id")
        genre["verbose_name"] = genre["name"]
        genre["name"] = genre["name"].replace(" ", "")
        count = 0
        movies_by_genre[genre["name"]] = []
        for i, g in enumerate(reco_movies["genres"].iteritems()):
            # s'occuper de tous les genres existants pour un film
            for j in range(min(2, len(g[1]))):
                if g[1][j]["id"] == genre["id"]:
                    movies_by_genre[genre["name"]].append(
                        reco_movies.iloc[i, :].to_dict()
                    )
                    count += 1
        genres_list.append((genre, count))
    # supprimer les genres moins importants pour cet utilisateur
    genres_list.sort(key=lambda tup: tup[1], reverse=True)
    genres_list, genres_list_pop = (
        [g[0] for g in genres_list[:8]],
        [g[0] for g in genres_list[8:]],
    )
    for genre in genres_list_pop:
        movies_by_genre.pop(genre["name"])
    # rajouter des films random si pas assez de ce type avec la prediction
    for genre in genres_list:
        if len(movies_by_genre[genre["name"]]) < 15:
            for movie in Movie.filter(
                genres__name=genre["verbose_name"],
                limit=15 - len(movies_by_genre[genre["name"]]),
            ):
                movies_by_genre[genre["name"]].append(movie.json)

    return render_template(
        "movies.html",
        dict_reco_movies=dict_reco_movies,
        genres_list=genres_list,
        movies_by_genre=movies_by_genre,
    )


@app.route("/movies/movie=<int:movie_id>")
def movie(movie_id):
    if "username" not in session or "id" not in session:
        return redirect(url_for("index"))
    movie = Movie.get(id=movie_id).json
    movie["globalRating"] = (
        float("{0:.2f}".format(movie["globalRating"]))
        if movie["globalRating"]
        else "Not rated yet"
    )
    user = User.get(username=session["username"])
    rating = Ratings.get(cinema=movie_id, user=user._mongo_id)
    my_rating = rating._rating if rating else "Not rated yet"
    return render_template("movie.html", movie=movie, my_rating=my_rating)


# TV Shows pages
@app.route("/tvshows", methods=["GET"])
def tvshows():
    if "username" not in session or "id" not in session:
        return redirect(url_for("index"))
    genres_list = []
    tvshows_by_genre = {}
    for genre in genres_tvshow_db.find():
        genre.pop("_id")
        genre["verbose_name"] = genre["name"]
        genre["name"] = genre["name"].replace(" ", "").replace("&", "")
        genres_list.append(genre)
        tvshows_by_genre[genre["name"]] = []
        # add well-known tv shows (no reco for tv shows)
        for tvshow in TVShow.filter_and_sort(
            genres=genre["id"], limit=15, sort=[("vote_count", -1)]
        ):
            tvshows_by_genre[genre["name"]].append(tvshow.json)
    return render_template(
        "tvshows.html", genres_list=genres_list, tvshows_by_genre=tvshows_by_genre
    )


@app.route("/tvshows/tvshow=<int:tvshow_id>")
def tvshow(tvshow_id):
    if "username" not in session or "id" not in session:
        return redirect(url_for("index"))
    tvshow = TVShow.get(id=tvshow_id).json
    tvshow["globalRating"] = (
        float("{0:.2f}".format(tvshow["globalRating"]))
        if tvshow["globalRating"]
        else "Not rated yet"
    )
    user = User.get(username=session["username"])
    rating = Ratings.get(cinema=tvshow_id, user=user._mongo_id)
    my_rating = rating._rating if rating else "Not rated yet"
    return render_template("tvshow.html", tvshow=tvshow, my_rating=my_rating)


# Profile page
@app.route("/profile", methods=["GET"])
def profile():
    if "username" not in session or "id" not in session:
        return redirect(url_for("index"))
    return render_template("profile.html")


### POST ROUTES

# Authentication
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    if User.get(username=username):
        flash("This user already exists")
        return home()
    else:
        user = User(username=username, emailAddress=email, password=password)
        user.save()
        user = User.get(username=username)
        session["username"] = username
        session["id"] = user.mongo_id
        return redirect(url_for("first_ratings"))


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = User.get(username=username, password=password)
    if user:
        session["username"] = username
        session["id"] = user.mongo_id
    else:
        flash("wrong password!")
    return home()


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    session.pop("id", None)
    return redirect(url_for("index"))


# Add rating
@app.route("/add_rating", methods=["POST"])
def add_rating():
    if "username" not in session:
        return "Not logged in"
    cinemaId = request.json["cinemaId"]
    rating = request.json["rating"]
    cinemaClass = Movie if cinemaId < 500000 else TVShow
    cinema = cinemaClass.get(id=cinemaId)
    user = User.get(username=session["username"])
    rat = Ratings(rating=rating, cinema=cinema, user=user)
    rat.save()
    return "done"


# Search
@app.route("/search_in_db", methods=["POST"])
def search_in_db():
    if "username" not in session:
        return "Not logged in"
    query = request.json["query"]
    movie_found = Movie.get(name=query)
    if movie_found:
        return url_for("movie", movie_id=str(movie_found._id))
    tvshow_found = TVShow.get(name=query)
    if tvshow_found:
        return url_for("tvshow", tvshow_id=str(tvshow_found._id))
    else:
        return "not found"

