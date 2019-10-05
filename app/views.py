import os
from flask import render_template, redirect, url_for,Flask
from flask_pymongo import PyMongo
from flask import request
from flask import jsonify
import pandas as pd
from flask_migrate import Migrate
from app.classes.movies_and_series import *
from app.classes.user import *
from app.classes.ratings import *

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
#app.config['MONGO_URI'] = os.environ.get('MONGODB_URI')
app.config['MONGO_URI'] = 'mongodb://heroku_1hj3v1h2:hiiq0l9nuj1fdffsqffr6spc1p@ds113799.mlab.com:13799/heroku_1hj3v1h2?retryWrites=false'

mongo = PyMongo(app)
migrate = Migrate(app, mongo)

@app.route('/')
def home(name=None):
    return redirect(url_for('index'))


@app.route('/index')
def index(name=None):
    a=TVShow(name='barth_serie_test')
    b=Season(name='test_season',number=1,tvShow=a)
    d=Season(name='test_season_2',number=2,tvShow=a)
    c=Episode(name='episode_test',number=1,runtime=100,season=b)
    barth=User(username='barth2501',emailAddress='barth@',password='eheh')
    r=Ratings(5,a,barth)
    return render_template('index.html', name=name)


@app.route('/movies')
def movies():
    genres = mongo.db.genres
    return render_template('movies.html', genres=genres)

@app.route('/movies/genre=<int:genre_id>')
def genre(genre_id):
    movies = mongo.db.movies
    return render_template('genre.html', movies = movies, genre_id=genre_id)

@app.route('/movie', methods = ['POST'])
def add_movie():
    movie = mongo.db.movies
    try :
        name = request.json['name']
        description = request.json['description']
        movie_id = movie.insert({'name':name,'description':description})
        new_movie = movie.find_one({'_id': movie_id })
        output = {'name' : new_movie['name']}
        return jsonify({'result' : output})
    except TypeError:
        return jsonify({'result' : 'niet'})

@app.route('/movie', methods = ['GET'])
def all_movie():
    movie = mongo.db.movies
    output = []
    for s in movie.find():
        try:
            output.append({
            'original_title':s['original_title']
        })
        except KeyError:
            continue
    return jsonify({'result' : output})