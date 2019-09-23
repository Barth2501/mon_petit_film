class Ratings:
    def __init__(self, rating, ratedObject, user):
        self._rating = rating
        self._user = user
        user._addRating(self)
        self._ratedObject = ratedObject
        ratedObject._addRating(self)
