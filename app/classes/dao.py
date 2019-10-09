from pymongo import MongoClient

URI = "mongodb://heroku_1hj3v1h2:hiiq0l9nuj1fdffsqffr6spc1p@ds113799.mlab.com:13799/heroku_1hj3v1h2?retryWrites=false"
client = MongoClient(URI)
db = client.get_default_database()


class DAO:
    _collection = None

    @classmethod
    def all(cls):
        if not isinstance(cls._collection, str):
            cls._collection = cls.__name__.lower()
        return [cls(**instance) for instance in db[cls._collection].find()]

    @classmethod
    def filter(cls, **kwargs):
        if not isinstance(cls._collection, str):
            cls._collection = cls.__name__.lower()
        filters = {}
        for key in kwargs.keys():
            filters[key.replace('__', '.')] = kwargs[key]
        return [cls(**instance) for instance in db[cls._collection].find(filters)]

    @classmethod
    def get(cls, **kwargs):
        if not isinstance(cls._collection, str):
            cls._collection = cls.__name__.lower()
        filters = {}
        for key in kwargs.keys():
            filters[key.replace('__', '.')] = kwargs[key]
        found = db[cls._collection].find_one(filters)
        return cls(**found) if found else None

    @classmethod
    def insert_or_update_one(cls, **kwargs):
        return cls(**kwargs).save()

    def save(self):
        if not isinstance(type(self)._collection, str):
            type(self)._collection = type(self).__name__.lower()
        if not self._mongo_id:
            instance_from_db = type(self).get(name=self._name)
            if instance_from_db:
                self._mongo_id = instance_from_db._mongo_id
        if self._mongo_id:
            return db[type(self)._collection].replace_one({'_id': self._mongo_id}, self.json)
        else:
            return db[type(self)._collection].insert_one(self.json)

    def delete(self):
        if not isinstance(type(self)._collection, str):
            type(self)._collection = type(self).__name__.lower()
        deleted_in_db = False
        if self._mongo_id:
            db[type(self)._collection].delete_one({'_id': self._mongo_id})
            deleted_in_db = True
        return deleted_in_db
