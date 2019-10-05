import pymongo
          
          
class DB(object):
          
    URI = "mongodb://heroku_1hj3v1h2:hiiq0l9nuj1fdffsqffr6spc1p@ds113799.mlab.com:13799/heroku_1hj3v1h2?retryWrites=false"
          
    @staticmethod
    def init():
        client = pymongo.MongoClient(DB.URI)
        DB.DATABASE = client.get_default_database()                                                                                                                                   
          
    @staticmethod
    def insert(collection, data):
        DB.DATABASE[collection].insert(data)
          
    @staticmethod
    def find_one(collection, query):
        return DB.DATABASE[collection].find_one(query)

    @staticmethod
    def update_one(collection, query,new_values):
        return DB.DATABASE[collection].update_one(query, new_values)
        