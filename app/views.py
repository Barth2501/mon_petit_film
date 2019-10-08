# import os
from flask import render_template, redirect, url_for, Flask, request, jsonify
from flask_pymongo import PyMongo
from flask import request
from flask import jsonify
import pandas as pd
import json
from flask_migrate import Migrate
from app.classes.movies_and_series import *
from app.classes.user import *
from app.classes.ratings import *
from flask_login import LoginManager

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
# app.config['MONGO_URI'] = os.environ.get('MONGODB_URI')
app.config['MONGO_URI'] = 'mongodb://heroku_1hj3v1h2:hiiq0l9nuj1fdffsqffr6spc1p@ds113799.mlab.com:13799/heroku_1hj3v1h2?retryWrites=false'

mongo = PyMongo(app)
genres_db = mongo.db.genres
movies_db = mongo.db.movies

login = LoginManager(app)

@app.route('/')
def home(name=None):
    return redirect(url_for('index'))


@app.route('/index')
def index(name=None):
    # with open('movies.txt', 'r') as data_file:
    #     json_data = data_file.read()
    # datas = json.loads(json_data)
    # for data in datas:
    #     a=Movie(name=data['original_title'], overview=data['overview'], homepage=data['homepage'], id=data['id'], poster_path=data['poster_path'], release_date=data['release_date'], genres=data['genres'], globalRating=data['vote_average'], runtime=data['runtime'])
    return render_template('index.html', name=name)

@app.route('/movies')
def movies():
    genres_list = []
    movies_by_genre = {}
    for genre in genres_db.find():
        genre.pop('_id')
        genres_list.append(genre)
        movies_by_genre[genre['name']] = []
        for movie in movies_db.find({'genres.id': genre['id']}).limit(12):
            movie.pop('_id')
            movies_by_genre[genre['name']].append(movie)
    return render_template('movies.html', genres_list=genres_list, movies_by_genre=movies_by_genre)


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
