class Ratings():

    ratingId = 1

    def __init__(self,userId,globalId, rating):
        self._ratingId = Ratings.ratingId
        self._userId = userId
        self._globalId = globalId
        self._rating = rating
        Ratings.ratingId += 1
    
    @property
    def userId(self):
        return self._userId

    @property
    def globalId(self):
        return self._globalId

    @property
    def rating(self):
        return self._rating