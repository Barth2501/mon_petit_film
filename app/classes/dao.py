from pymongo import MongoClient

# We use a mongo database hosted on heroku, and interact with it using the DAO class
URI = "mongodb://heroku_1hj3v1h2:hiiq0l9nuj1fdffsqffr6spc1p@ds113799.mlab.com:13799/heroku_1hj3v1h2?retryWrites=false"
client = MongoClient(URI)
db = client.get_default_database()


# DAO is a class used as an interface to call mongo database from python.
# It is an "abstract" class, we never create DAO instance (though it is possible)
# When creating an instance of movie / tvshow, being a child of DAO all functions can be used,
#   it allows us to call save or delete method straight from the movie instance
# We also use its class methods directly to find a specific movie/tvshow, update... in the matching database
class DAO:
    _collection = None

    @classmethod
    def all(cls):
        return [cls(**instance) for instance in db[cls._collection].find()]

    @classmethod
    def all_values_list(cls, **kwargs):
        columns = {}
        for key in kwargs.keys():
            columns[key.replace("__", ".")] = kwargs[key]
        return db[cls._collection].find({}, columns)

    @classmethod
    def filter(cls, limit=0, **kwargs):
        filters = {}
        for key in kwargs.keys():
            filters[key.replace("__", ".")] = kwargs[key]
        return [
            cls(**instance)
            for instance in db[cls._collection].find(filters).limit(limit)
        ]

    @classmethod
    def filter_and_sort(cls, sort, limit=0, **kwargs):
        filters = {}
        for key in kwargs.keys():
            filters[key.replace("__", ".")] = kwargs[key]
        return [
            cls(**instance)
            for instance in db[cls._collection].find(filters).sort(sort).limit(limit)
        ]

    @classmethod
    def filter_json(cls, limit=0, **kwargs):
        filters = {}
        for key in kwargs.keys():
            filters[key.replace("__", ".")] = kwargs[key]
        return [
            cls(**instance).json
            for instance in db[cls._collection].find(filters).limit(limit)
        ]

    @classmethod
    def get(cls, **kwargs):
        filters = {}
        for key in kwargs.keys():
            filters[key.replace("__", ".")] = kwargs[key]
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

    @classmethod
    def find_many(cls, query={}, projection={}):
        return db[cls._collection].find(query, projection)

    def save(self):
        if not self._mongo_id:
            instance_from_db = type(self).get(name=self._name)
            if instance_from_db:
                self._mongo_id = instance_from_db._mongo_id
        if self._mongo_id:
            return type(self).replace_one({"_id": self._mongo_id}, {"$set": self.json})
        else:
            return type(self).insert_one(self.json)

    def delete(self):
        deleted_in_db = False
        if self._mongo_id:
            type(self).delete_one({"_id": self._mongo_id})
            deleted_in_db = True
        return deleted_in_db
