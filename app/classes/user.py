from app.classes.dao import DAO
from bson.objectid import ObjectId


class User(DAO):
    _collection = 'user'

    def __init__(self, username, emailAddress, password, **kwargs):
        self._mongo_id = ObjectId(kwargs.get('_id')) if kwargs.get('_id', None) else None
        self._username = username
        self._emailAddress = emailAddress
        self._password = password
        self._ratings = kwargs.get('ratings', [])

    def save(self):
        if not self._mongo_id:
            instance_from_db = User.get(username=self._username)
            if instance_from_db:
                self._mongo_id = instance_from_db._mongo_id
        if self._mongo_id:
            return User.replace_one({'_id': self._mongo_id}, self.json)
        else:
            return User.insert_one(self.json)

    def delete(self):
        deleted_in_db = False
        instance_from_db = User.get(username=self._username)
        if instance_from_db:
            User.delete_one({'_id': instance_from_db._mongo_id})
            deleted_in_db = True
        return deleted_in_db

    def _addRating(self, cinemaId, rating):
        if not self._mongo_id:
            instance_from_db = User.get(username=self._username)
            if instance_from_db:
                self._mongo_id = instance_from_db._mongo_id
                self._ratings = instance_from_db._ratings
        newRating = {'cinema': cinemaId, 'rating': rating}
        self._ratings.append(newRating)
        if self._mongo_id:
            return User.update_one({'_id': self._mongo_id}, {'$push': {'ratings': newRating}})

    @property
    def mongo_id(self):
        return str(self._mongo_id)
        
    @property
    def json(self):
        return {
            'username': self._username,
            'emailAddress': self._emailAddress,
            'password': self._password,
            'ratings': self._ratings,
        }

    @property
    def username(self):
        return self._username
