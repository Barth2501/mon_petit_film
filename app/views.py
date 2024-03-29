from flask import render_template, redirect, url_for, Flask, request, session, flash
from flask_pymongo import PyMongo
from app.classes.user import User
from app.classes.ratings import Ratings
from app.classes.movies_and_series import Cinema, Movie, TVShow
from app.svd import recommend_movies
import random
from flask_mail import Mail
import app.config as config
import re


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
        film = movies[random.randint(0, len(movies)-1)].json
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
    if "username" not in session or "id" not in session:
        return redirect(url_for("index"))
    reco_movies = recommend_movies(session["id"], 80)[1]
    dict_reco_movies = reco_movies.to_dict("records")
    genres_list = []
    movies_by_genre = {}
    # on commence par ajouter les films recommandés pour chaque genre
    for genre in genres_db.find():
        genre.pop("_id")
        genre["verbose_name"] = genre["name"]
        genre["name"] = genre["name"].replace(" ", "")
        count = 0
        movies_by_genre[genre["name"]] = []
        for i, g in enumerate(reco_movies["genres"].iteritems()):
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
    # rajouter des films random si pas assez de ce genre avec la prediction
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
    # on récupère le film demandé et les ratings associés
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
    # on récupère pour chaque genre les séries les plus connues (reco que pour les films)
    for genre in genres_tvshow_db.find():
        genre.pop("_id")
        genre["verbose_name"] = genre["name"]
        genre["name"] = genre["name"].replace(" ", "").replace("&", "")
        genres_list.append(genre)
        tvshows_by_genre[genre["name"]] = []
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
    # on récupère la série demandée et les ratings associés
    tvshow = TVShow.get(id=tvshow_id).json
    tvshow["globalRating"] = (
        float("{0:.2f}".format(tvshow["globalRating"]))
        if tvshow["globalRating"]
        else "Not rated yet"
    )
    user = User.get(username=session["username"])
    rating = Ratings.get(cinema=tvshow_id, user=user._mongo_id)
    my_rating = rating._rating if rating else "Not rated yet"
    # deal with all potentials javascript parsing problems
    tvshow.pop("ratings")
    tvshow["overview"] = tvshow["overview"].replace('"', "'")
    for i, season in enumerate(tvshow["seasons"]):
        tvshow["seasons"][i]["verbose_name"] = season["name"]
        tvshow["seasons"][i]["name"] = season["name"].replace(" ", "").replace("&", "")
        tvshow["seasons"][i].pop("overview")
        for j in range(len(season["episodes"])):
            tvshow["seasons"][i]["episodes"][j].pop("overview")
        tvshow["seasons"][i]["number_of_slides"] = int(
            (len(season["episodes"]) + 4) / 5
        )
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


# Send reco mail to new user
@app.route("/send_mail")
def send_mail():
    from cronjobs.celery import send_mail_user

    send_mail_user.delay(session["username"], session["id"])
    return "done"


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
    # search for the best matching movie and tv show
    name = re.compile("^" + re.escape(query) + "$", re.IGNORECASE)
    movie_found = Movie.get(name=name)
    if not movie_found:
        name = re.compile("^" + re.escape(query), re.IGNORECASE)
        movies_found = Movie.filter_and_sort(name=name, sort=[("vote_count", -1)])
        if len(movies_found):
            movie_found = movies_found[0]
        if not movie_found:
            name = re.compile(re.escape(query), re.IGNORECASE)
            movies_found = Movie.filter_and_sort(name=name, sort=[("vote_count", -1)])
            if len(movies_found):
                movie_found = movies_found[0]
    tvshow_found = TVShow.get(name=name)
    if not tvshow_found:
        name = re.compile("^" + re.escape(query), re.IGNORECASE)
        tvshows_found = TVShow.filter_and_sort(name=name, sort=[("vote_count", -1)])
        if len(tvshows_found):
            tvshow_found = tvshows_found[0]
        if not tvshow_found:
            name = re.compile(re.escape(query), re.IGNORECASE)
            tvshows_found = TVShow.filter_and_sort(name=name, sort=[("vote_count", -1)])
            if len(tvshows_found):
                tvshow_found = tvshows_found[0]
    # return the best query matching between two results
    if movie_found and tvshow_found:
        if movie_found._name.lower() != tvshow_found._name.lower():
            if movie_found._name.lower() == query.lower():
                return url_for("movie", movie_id=str(movie_found._id))
            if tvshow_found._name.lower() == query.lower():
                return url_for("tvshow", tvshow_id=str(tvshow_found._id))
    # return the one with higher vote_count
    if (not movie_found) and (not tvshow_found):
        return "not found"
    if (not tvshow_found) or (
        movie_found and movie_found._vote_count > tvshow_found._vote_count
    ):
        return url_for("movie", movie_id=str(movie_found._id))
    if (not movie_found) or (
        tvshow_found and movie_found._vote_count < tvshow_found._vote_count
    ):
        return url_for("tvshow", tvshow_id=str(tvshow_found._id))
    # if similar, return movie
    return url_for("movie", movie_id=str(movie_found._id))
