# mon_petit_film



## How to launch the MyBigMovie app
To launch the app, you will have to build the docker image after cloning the project with:
```
$ cd mon_petit_film/
$ (sudo) docker-compose build
$ (sudo) docker-compose up -d
```
Then go to your localhost:8000

## Features

### Database and DAO
We use a mongo database hosted on Heroku. We register on this database every user, rating, movie and tvshows.
We interact with this database using a DAO class and pymongo.

### Authentication
Each user can create its own profile, regarding the movies and tvshows he likes.
After signing up, you will have to give a mark to some movies in order to build your recommendation profile.
N.B: If you haven't seen the movie you can click on the slashed eye next to the star.

### Movies
We have more than 20k movies saved in our database, and you can search for one of them, knowing its name or its ganre, and give a rating to the ones you like. You will notice that the movies are sorted by your recommendations on the movies page.

### TVshows
We have more than 1k tvshows saved on our database, and all the seasons and episodes associated to them. You can rate them but our recommendation engine doesn't work on tvshows.

### Ratings
We register every ratings on our database. 
We also have recorded 1 million ratings from an API in order to build the recommendation engine. (in the rating_update.csv file)

### Cronjobs
A register user will receive every monday morning at 8am (UTC) an email with 5 recommended movies for this week. He will also receive this email after signing up.

### Docker
The docker compose file will build and run in the same time three dockers in parallel. One for the app, one for the celery cronjobs and one for redis socket.

## Architecture

### Classes
We registered all of our class architecture in the app/classes folder.
We have a DAO class for interaction with database, and a class for every entity used in our website.

### Static
We registered every static file in the app/static folder.
We have used a bootstrap template and some jquery components.

### Templates
We registered every HTML template in the app/templates folder.

### Celery
The cronjobs files are located in the cronjobs folder

### Backend
The backend python files are located in the app folder.
We use a flask app in the views.py file, and our recommendation algorithm is located in the svd.py file
