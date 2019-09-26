from flask import render_template, redirect, url_for,Flask

app = Flask(__name__)

@app.route('/')
def home(name=None):
    return redirect(url_for('index'))

@app.route('/index')
def index(name=None):
    return render_template('index.html', name=name)

@app.route('/movies')
def movies():
    return render_template('movies.html', context={})