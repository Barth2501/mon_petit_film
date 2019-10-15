from app.classes.dao import DAO


class Ratings(DAO):
    _collection = 'ratings'

    def __init__(self, rating, cinema, user):
        self._rating = rating
        self._user = user
        self._cinema = cinema

    def save(self):
        instance_from_db = Ratings.get(cinema=self._cinema._id, user=self._user._id)
        if instance_from_db:
            return Ratings.replace_one({'_id': instance_from_db._mongo_id}, self.json)
        else:
            return Ratings.insert_one(self.json)
        self._user._addRating(self._cinema._id, self._rating)
        self._cinema._addRating(self._user._id, self._rating)

    def delete(self):
        deleted_in_db = False
        instance_from_db = Ratings.get(cinema=self._cinema._id, user=self._user._id)
        if instance_from_db:
            Ratings.delete_one({'_id': instance_from_db._mongo_id})
            deleted_in_db = True
        return deleted_in_db

    @property
    def json(self):
        return {
            'user': self._user._id,
            'cinema': self._cinema._id,
            'rating': self._rating,
        }
