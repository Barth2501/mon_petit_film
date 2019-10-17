# import os
from flask import render_template, redirect, url_for, Flask, request, jsonify, session, flash
from flask_pymongo import PyMongo
from app.classes.user import User
from app.classes.ratings import Ratings
from app.classes.movies_and_series import Cinema, Movie
import pandas as pd
from app.svd import recommend_movies
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
# app.config['MONGO_URI'] = os.environ.get('MONGODB_URI')
app.config['MONGO_URI'] = 'mongodb://heroku_1hj3v1h2:hiiq0l9nuj1fdffsqffr6spc1p@ds113799.mlab.com:13799/heroku_1hj3v1h2?retryWrites=false'

mongo = PyMongo(app)
genres_db = mongo.db.genres
movies_db = mongo.db.movies


@app.route('/')
def home():
    return redirect(url_for('index'))


@app.route('/index')
def index():
    username = None
    if 'username' in session:
        username = session['username']
    return render_template('index.html', username=username)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if User.get(username=username, password=password):
        session['username'] = username
    else:
        username = request.form['username']
        password = request.form['password']
        user = User.get(username=username, password=password)
        if user:
            session['username'] = username
            session['id'] = user.mongo_id
        else:
            flash('wrong password!')
        return home()


@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign_up.html')
    else:
        username = request.form['inputName']
        password = request.form['inputPassword']
        passwordBis = request.form['inputPasswordBis']
        email = request.form['inputEmail']
        if password != passwordBis:
            flash('The two password don\'t match')
            return redirect(url_for('signup'))
        elif User.get(username=username):
            flash('This user already exists')
            return redirect(url_for('signup'))
        else:
            user = User(username=username, emailAddress=email, password=password)
            user.save()
            session['username'] = username
            session['id'] = user.mongo_id
            return redirect(url_for('first_ratings', username=user.json['username']))



@app.route('/first_ratings/username=<username>')
def first_ratings(username):
    film_sample = []
    poster_sample = []
    id_sample = []
    for i in range(10):
        try:
            film = Movie.get(id=i).json
            film_sample.append(film)
            poster_sample.append(film['poster_path'])
            id_sample.append(film['id'])
        except AttributeError:
            continue
    return render_template('first_ratings.html', film_sample=film_sample, poster_sample=poster_sample, id_sample=id_sample, username=username)

@app.route('/add_rating/username=<username>', methods=['GET', 'POST'])
def add_rating(username):
    if request.method == 'POST':
        movieId = request.json['movieId']
        rating = request.json['rating']
        cinema = Movie.get(id=movieId)
        user = User.get(username=username)
        rat = Ratings(rating, cinema, user)
        rat.save()
    return 'bravo'

@app.route('/movies')
def movies():
    reco_movies = recommend_movies(session['id'], 100)[1]
    dict_reco_movies = reco_movies.to_dict('records')
    genres_list = []
    movies_by_genre = {}
    for genre in genres_db.find():
        genre.pop('_id')
        count = 0
        movies_by_genre[genre['name']] = []
        for i,g in enumerate(reco_movies['genres'].iteritems()):
            for j in range(min(2,len(g[1]))):
                if g[1][j]['id']==genre['id']:
                    movies_by_genre[genre['name']].append(reco_movies.iloc[i,:].to_dict())
                    count += 1
        genres_list.append((genre,count))
    genres_list.sort(key=lambda tup: tup[1], reverse = True)
    return render_template('movies.html', dict_reco_movies=dict_reco_movies, genres_list=genres_list, movies_by_genre=movies_by_genre)


@app.route('/movies/genre=<int:genre_id>')
def genre(genre_id):
    movies = mongo.db.movies
    return render_template('genre.html', movies=movies, genre_id=genre_id)


@app.route('/movie', methods=['POST'])
def add_movie():
    movie = mongo.db.movies
    try:
        name = request.json['name']
        description = request.json['description']
        movie_id = movie.insert({'name': name, 'description': description})
        new_movie = movie.find_one({'_id': movie_id})
        output = {'name': new_movie['name']}
        return jsonify({'result': output})
    except TypeError:
        return jsonify({'result': 'niet'})


@app.route('/movie', methods=['GET'])
def all_movie():
    movie = mongo.db.movies
    output = []
    for s in movie.find():
        try:
            output.append({
                'original_title': s['original_title']
            })
        except KeyError:
            continue
    return jsonify({'result': output})


# from app.collab_filter import movie_rating_merged_data

# @app.route('/collab_filter')
# def colab_filter():
#     #for movie in movies_db.find():
#     #    id = movie['id']
#     #    try:
#     #        DB.update_one(collection='movies', query={'id': id}, new_values= {'$set': {'id':int(id)}})
#     #    except ValueError:
#     #        DB.delete_one(collection='movies',query={'id':id})
#     print(movie_rating_merged_data)
#     pass
