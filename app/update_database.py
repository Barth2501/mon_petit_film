from classes.movies_and_series import *
import itertools


def delete_id_null():
    for cine in Cinema.filter(id=None):
        cine.delete()


def update_vote_average_null():
    for movie in Movie.filter(vote_average=None):
        movie._vote_average = 0
        movie._vote_count = 0
        movie.save()
        print("yes")


def update_vote_average_0():
    for movie in Movie.find_many({"vote_average": 0, "vote_count": {"$gte": 1500}}):
        movie = Movie(**movie)
        movie._vote_average = 7.5
        movie.save()
        print(movie._name)


def update_rating_and_vote_average():
    for movie in TVShow.all():
        ratings_count = len(movie._ratings)
        global_rating = (
            movie._globalRating if ratings_count and movie._globalRating else 0
        )
        vote_average = movie._vote_average / 2
        vote_count = int(movie._vote_count / 400) + 1

        movie._vote_average = vote_average
        movie._globalRating = (
            ratings_count * global_rating + vote_count * vote_average
        ) / (ratings_count + vote_count)

        print(movie._name, "\t\t", movie._globalRating)
        movie.save()


def copy_cinema_in_movies():
    i = 0
    for movie in Movie.all():
        i += 1
        new_movie = NewMovie(**movie.json)
        new_movie.save()
        print(i)


def add_vote_count():
    i = itertools.count(0)
    for movie in Cinema.find_many(projection={"id": 1, "vote_count": 1}):
        Movie.update_one(
            {"id": movie["id"]}, {"$set": {"vote_count": movie["vote_count"]}}
        )
        print(next(i))


update_rating_and_vote_average()
