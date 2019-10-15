# import os
from flask import render_template, redirect, url_for, Flask, request, jsonify, session, flash
from flask_pymongo import PyMongo
from app.classes.user import User

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


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        if User.get(username=username, password=password):
            session['username'] = username
        else:
            flash('wrong password!')
        return home()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
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
            session['username'] = username
            return redirect(url_for('index'))


@app.route('/test')
def test():
    return render_template('first_ratings.html')


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
