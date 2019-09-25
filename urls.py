from flask import Flask
from flask import render_template,url_for

app = Flask(__name__)


@app.route('/')
def index(name=None):
    return render_template('index.html', name=name)

@app.route('/movies')
def movies():
    return render_template('movies.html', context={})
