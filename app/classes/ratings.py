from app.classes.dao import DAO
from bson.objectid import ObjectId


# The class Ratings is a child of DAO in order to be able to interact with database.
# It uses the collection 'ratings'
# A rating is the link between a user and a movie/tvshow, with an associated value
# We redefine here some DAO methods because it does not work the same way for ratings
class Ratings(DAO):
    _collection = "ratings"

    def __init__(self, **kwargs):
        self._mongo_id = (
            ObjectId(kwargs.get("_id")) if kwargs.get("_id", None) else None
        )
        self._rating = kwargs.get("rating", 0)
        self._user = kwargs.get("user", None)
        self._cinema = kwargs.get("cinema", None)

    # when saving a new rating, we add it to its relative user and cinema instances
    def save(self):
        self._user._addRating(self._cinema._id, self._rating)
        self._cinema._addRating(self._user._mongo_id, self._rating)
        instance_from_db = Ratings.get(
            cinema=self._cinema._id, user=self._user._mongo_id
        )
        if instance_from_db:
            return Ratings.replace_one(
                {"_id": instance_from_db._mongo_id}, {"$set": self.json}
            )
        else:
            return Ratings.insert_one(self.json)

    def delete(self):
        deleted_in_db = False
        instance_from_db = Ratings.get(cinema=self._cinema._id, user=self._user._id)
        if instance_from_db:
            Ratings.delete_one({"_id": instance_from_db._mongo_id})
            deleted_in_db = True
        return deleted_in_db

    @property
    def json(self):
        return {
            "user": self._user._mongo_id,
            "cinema": self._cinema._id,
            "rating": self._rating,
        }
