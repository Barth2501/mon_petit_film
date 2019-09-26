<<<<<<< HEAD
from flask import render_template, redirect, url_for,Flask
=======
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
>>>>>>> e4e67aa3c627b76392bebed62f5c85830fcf1c87

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