import os
from flask import render_template, redirect, url_for,Flask
from flask_pymongo import PyMongo
from flask import request
from flask import jsonify
import pandas as pd

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
#app.config['MONGO_URI'] = os.environ.get('MONGODB_URI')
app.config['MONGO_URI'] = 'mongodb://heroku_1hj3v1h2:hiiq0l9nuj1fdffsqffr6spc1p@ds113799.mlab.com:13799/heroku_1hj3v1h2?retryWrites=false'

mongo = PyMongo(app)


@app.route('/')
def home(name=None):
    return redirect(url_for('index'))


@app.route('/index')
def index(name=None):
    return render_template('index.html', name=name)


@app.route('/movies')
def movies():
    genres = mongo.db.genres
    #genres = pd.DataFrame(list(genres.find()))
    # for genre in genres.find():
    #     print(genre['name'])
    return render_template('movies.html', genres=genres)

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
        print(s)
        try:
            output.append({
            'original_title':s['original_title']
        })
        except KeyError:
            continue
    return jsonify({'result' : output})