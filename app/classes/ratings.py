from app.database import DB
from app.classes.movies_and_series import *
from app.classes.dao import DAO

class Ratings(DAO):
    __tablename__ = 'ratings'

    def __init__(self, rating, cinema, user):
        self._rating = rating
        self._user = user
        self._cinema = cinema
        user._addRating(cinema.name, rating)
        cinema._addRating(user.username, rating)
        if not DB.find_one('ratings', query={'user': user.username,'cinema': cinema.name}):
            DB.insert(collection='ratings', data = {
                'cinema': cinema.name,
                'user': user.username,
                'rating': rating
            })

    @property
    def json(self):
        return {
            'user': self._user.json,
            'cinema': self._cinema,
            'rating': self._rating,
        }