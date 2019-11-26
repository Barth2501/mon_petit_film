from .dao import DAO
from bson.objectid import ObjectId
from statistics import mean


# The class Cinema is a child of DAO in order to be able to interact with database.
# It is an "abstract" class, we never create Cinema instance (though it is possible)
# We instanciate in this class every needed properties and methods for movies and tvshows.
# It has two childs, Movie and TVShow which use all properties from Cinema
class Cinema(DAO):
    _collection = "cinema"

    def __init__(self, name, **kwargs):
        self._id = kwargs.get("id", None)
        self._mongo_id = (
            ObjectId(kwargs.get("_id")) if kwargs.get("_id", None) else None
        )
        self._name = name
        self._overview = kwargs.get("overview", "")
        self._homepage = kwargs.get("homepage", "")
        self._poster_path = kwargs.get("poster_path", "")
        self._release_date = kwargs.get("release_date", None)
        self._makers = kwargs.get("makers", [])
        self._producers = kwargs.get("producers", [])
        self._actors = kwargs.get("actors", [])
        self._genres = kwargs.get("genres", [])
        self._vote_average = kwargs.get("vote_average", 0)
        self._vote_count = kwargs.get("vote_count", 0)
        self._globalRating = kwargs.get(
            "globalRating", kwargs.get("vote_average", None)
        )
        self._ratings = kwargs.get("ratings", [])

    # Method used to rate a movie/tvshow. It also updates the global rating of the instance
    def _addRating(self, userId, rating):
        # check if user already rated this cinema instance, and update/insert rating consequently
        alreadyExist = type(self).get(id=self._id, ratings__user=userId)
        if alreadyExist:
            type(self).update_one(
                {"_id": alreadyExist._mongo_id, "ratings.user": userId},
                {"$set": {"ratings.$.rating": rating}},
            )
        else:
            newRating = {"user": userId, "rating": rating}
            self._ratings.append(newRating)
            self.save()
        # update instance with data from database
        instance_from_db = type(self).get(id=self._id)
        if instance_from_db:
            self._mongo_id = instance_from_db._mongo_id
            self._ratings = instance_from_db._ratings
            self._vote_average = instance_from_db._vote_average
            self._vote_count = instance_from_db._vote_count
        # compute global rating using a reduced weight for vote_average from api
        self._globalRating = mean(rating["rating"] for rating in self._ratings)
        ratings_count = len(self._ratings)
        vote_average = self._vote_average
        vote_count = int(self._vote_count / 400) + 1
        self._globalRating = (
            ratings_count * self._globalRating + vote_count * vote_average
        ) / (ratings_count + vote_count)
        # update global rating in database
        return type(self).update_one(
            {"_id": self._mongo_id}, {"$set": {"globalRating": self._globalRating}},
        )

    @property
    def name(self):
        return self._name

    @property
    def mongo_id(self):
        return str(self._mongo_id)


# Movie class, child of Cinema.
# Use mongo collection 'movies'
class Movie(Cinema):
    _collection = "movies"

    def __init__(self, name, runtime, **kwargs):
        Cinema.__init__(self, name, **kwargs)
        self._runtime = kwargs.get("runtime", 0)

    # json property returns for an instance a dictionnary of all useful properties
    @property
    def json(self):
        return {
            "name": self._name,
            "overview": self._overview,
            "homepage": self._homepage,
            "id": self._id,
            "poster_path": self._poster_path,
            "release_date": self._release_date,
            "makers": self._makers,
            "producers": self._producers,
            "actors": self._actors,
            "genres": self._genres,
            "vote_average": self._vote_average,
            "vote_count": self._vote_count,
            "globalRating": self._globalRating,
            "runtime": self._runtime,
            "ratings": self._ratings,
        }


# TVShow class, child of Cinema.
# Use mongo collection 'tvshows'
class TVShow(Cinema):
    _collection = "tvshows"

    def __init__(self, name, **kwargs):
        Cinema.__init__(self, name, **kwargs)
        self._seasons = kwargs.get("seasons", [])
        self._episodeLength = kwargs.get("episodeLength", "")

    # json property returns for an instance a dictionnary of all useful properties
    @property
    def json(self):
        return {
            "name": self._name,
            "overview": self._overview,
            "homepage": self._homepage,
            "id": self._id,
            "poster_path": self._poster_path,
            "release_date": self._release_date,
            "makers": self._makers,
            "producers": self._producers,
            "actors": self._actors,
            "genres": self._genres,
            "vote_average": self._vote_average,
            "vote_count": self._vote_count,
            "ratings": self._ratings,
            "globalRating": self._globalRating,
            "seasons": self._seasons,
        }

    # method to add a season object to a tvshow instance and save in db
    def _addSeasonToDB(self, season):
        # update seasons current state in database
        instance_from_db = self
        if not self._mongo_id:
            instance_from_db = TVShow.get(name=self._name)
        else:
            instance_from_db = TVShow.get(_id=self._mongo_id)
        self._mongo_id = instance_from_db._mongo_id
        self._seasons = instance_from_db._seasons
        # add season
        self._seasons.append(season.json)
        # determine episode length
        self._episodeLength = mean(
            episode["runtime"] for s in self._seasons for episode in s["episodes"]
        )
        # save in database
        if self._mongo_id:
            return TVShow.update_one(
                {"_id": self._mongo_id},
                {
                    "$addToSet": {"seasons": season.json},
                    "$set": {"episodeLength": self._episodeLength},
                },
            )

    # method to add an episode object to a tvshow instance and save in db
    def _addEpisodeToDB(self, episode, season):
        # update seasons current state in database
        instance_from_db = self
        if not self._mongo_id:
            instance_from_db = TVShow.get(name=self._name)
        else:
            instance_from_db = TVShow.get(_id=self._mongo_id)
        self._mongo_id = instance_from_db._mongo_id
        self._seasons = instance_from_db._seasons
        # update this season episodes with database state
        season._episodes = self._seasons[season._number - 1]["episodes"]
        # add episode
        season._episodes.append(episode.json)
        self._seasons[season._number - 1] = season.json
        # determine episode length
        self._episodeLength = mean(
            episode["runtime"]
            for episode in season["episode"]
            for season in self._seasons
        )
        # save in database
        if self._mongo_id:
            return TVShow.update_one(
                {"_id": self._mongo_id, "seasons.number": season._number},
                {
                    "$addToSet": {"seasons.$.episodes": episode.json},
                    "$set": {"episodeLength": self._episodeLength},
                },
            )


# Class Season, similar to Cinema but not a child of DAO
# Used only to format properties and add it to a tvshow instance
class Season:
    def __init__(self, name, number, tvShow, **kwargs):
        self._name = name
        self._overview = kwargs.get("overview", "")
        self._homepage = kwargs.get("homepage", "")
        self._poster_path = kwargs.get("poster_path", "")
        self._release_date = kwargs.get("release_date", None)
        self._makers = kwargs.get("makers", [])
        self._producers = kwargs.get("producers", [])
        self._actors = kwargs.get("actors", [])
        self._genres = kwargs.get("genres", [])
        self._number = number
        self._episodes = kwargs.get("episodes", [])
        self._tvShow = tvShow

    # method to add an episode instance to a season instance (no database interaction)
    def _addEpisode(self, episode):
        self._episodes.append(episode.json)

    # json property returns for an instance a dictionnary of all useful properties
    @property
    def json(self):
        return {
            "name": self._name,
            "overview": self._overview,
            "homepage": self._homepage,
            "poster_path": self._poster_path,
            "release_date": self._release_date,
            "makers": self._makers,
            "producers": self._producers,
            "actors": self._actors,
            "genres": self._genres,
            "number": self._number,
            "episodes": self._episodes,
        }


# Class Season, similar to Cinema but not a child of DAO
# Used only to format properties and add it to a season/tvshow instance
class Episode:
    def __init__(self, name, number, season, **kwargs):
        self._name = name
        self._overview = kwargs.get("overview", "")
        self._homepage = kwargs.get("homepage", "")
        self._poster_path = kwargs.get("poster_path", "")
        self._release_date = kwargs.get("release_date", None)
        self._makers = kwargs.get("makers", [])
        self._producers = kwargs.get("producers", [])
        self._actors = kwargs.get("actors", [])
        self._genres = kwargs.get("genres", [])
        self._number = number
        self._runtime = kwargs.get("runtime", 0)
        self._season = season
        self._tvShow = season._tvShow

    # json property returns for an instance a dictionnary of all useful properties
    @property
    def json(self):
        return {
            "name": self._name,
            "overview": self._overview,
            "homepage": self._homepage,
            "poster_path": self._poster_path,
            "release_date": self._release_date,
            "makers": self._makers,
            "producers": self._producers,
            "actors": self._actors,
            "genres": self._genres,
            "number": self._number,
            "runtime": self._runtime,
        }

