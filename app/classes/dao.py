from pymongo import MongoClient

URI = "mongodb://heroku_1hj3v1h2:hiiq0l9nuj1fdffsqffr6spc1p@ds113799.mlab.com:13799/heroku_1hj3v1h2?retryWrites=false"
client = MongoClient(URI)
db = client.get_default_database()


class DAO:
    _collection = None

    @classmethod
    def all(cls):
        return [cls(**instance) for instance in db[cls._collection].find()]

    @classmethod
    def all_values_list(cls, **kwargs):
        filters = {}
        for key in kwargs.keys():
            filters[key.replace('__', '.')] = kwargs[key]
        return db[cls._collection].find({}, filters)

    @classmethod
    def filter(cls, **kwargs):
        filters = {}
        for key in kwargs.keys():
            filters[key.replace('__', '.')] = kwargs[key]
        return [cls(**instance) for instance in db[cls._collection].find(filters)]

    @classmethod
    def get(cls, **kwargs):
        filters = {}
        for key in kwargs.keys():
            filters[key.replace('__', '.')] = kwargs[key]
        found = db[cls._collection].find_one(filters)
        return cls(**found) if found else None

    @classmethod
    def replace_one(cls, query, json):
        return db[cls._collection].update_one(query, json)

    @classmethod
    def insert_one(cls, json):
        return db[cls._collection].insert_one(json)

    @classmethod
    def update_one(cls, query, operations):
        return db[cls._collection].update_one(query, operations)

    @classmethod
    def delete_one(cls, query):
        return db[cls._collection].delete_one(query)

    def save(self):
        if not self._mongo_id:
            instance_from_db = type(self).get(name=self._name)
            if instance_from_db:
                self._mongo_id = instance_from_db._mongo_id
        if self._mongo_id:
            return type(self).replace_one({'_id': self._mongo_id}, self.json)
        else:
            return type(self).insert_one(self.json)

    def delete(self):
        deleted_in_db = False
        if self._mongo_id:
            type(self).delete_one({'_id': self._mongo_id})
            deleted_in_db = True
        return deleted_in_db
