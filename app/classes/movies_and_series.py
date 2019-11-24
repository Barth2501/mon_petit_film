from .dao import DAO
from bson.objectid import ObjectId
from statistics import mean


class Cinema(DAO):
    _collection = 'cinema'

    def __init__(self, name, **kwargs):
        self._id = kwargs.get('id', None)
        self._mongo_id = ObjectId(kwargs.get(
            '_id')) if kwargs.get('_id', None) else None
        self._name = name
        self._overview = kwargs.get('overview', '')
        self._homepage = kwargs.get('homepage', '')
        self._poster_path = kwargs.get('poster_path', '')
        self._release_date = kwargs.get('release_date', None)
        self._makers = kwargs.get('makers', [])
        self._producers = kwargs.get('producers', [])
        self._actors = kwargs.get('actors', [])
        self._genres = kwargs.get('genres', [])
        self._vote_average = kwargs.get('vote_average', 0)
        self._ratings = kwargs.get('ratings', [])
        self._vote_count = kwargs.get('vote_count', 0)
        self._globalRating = kwargs.get('globalRating', kwargs.get('vote_average', None))

    def _addRating(self, userId, rating):
        # update instance with data from database
        if not self._mongo_id:
            instance_from_db = type(self).get(name=self._name)
            if instance_from_db:
                self._mongo_id = instance_from_db._mongo_id
                self._ratings = instance_from_db._ratings
        # add new rating
        newRating = {'user': userId, 'rating': rating}
        self._ratings.append(newRating)
        # compute global rating using a reduced weight for vote_average from api
        self._globalRating = mean(rating['rating'] for rating in self._ratings)
        ratings_count = len(self._ratings)
        vote_average = self._vote_average
        vote_count = int(self._vote_count / 400) + 1
        self._globalRating = (ratings_count*self._globalRating+vote_count*vote_average)/(ratings_count+vote_count)
        # if already rated by this user, change old rating - else just add the new one
        alreadyExist = type(self).get(id=self._id, ratings__user=userId)
        if alreadyExist:
            if self._mongo_id:
                return type(self).update_one({'_id': self._mongo_id, 'ratings.user': userId}, {'$set': {'ratings.$.rating': rating, 'globalRating': self._globalRating}})
        if self._mongo_id:
            return type(self).update_one({'_id': self._mongo_id}, {'$push': {'ratings': newRating}, '$set': {'globalRating': self._globalRating}})

    @property
    def name(self):
        return self._name

    @property
    def mongo_id(self):
        return str(self._mongo_id)


class Movie(Cinema):
    _collection = 'movies'

    def __init__(self, name, runtime, **kwargs):
        Cinema.__init__(self, name, **kwargs)
        self._runtime = kwargs.get('runtime', 0)

    @property
    def json(self):
        return {
            'name': self._name,
            'overview': self._overview,
            'homepage': self._homepage,
            'id': self._id,
            'poster_path': self._poster_path,
            'release_date': self._release_date,
            'makers': self._makers,
            'producers': self._producers,
            'actors': self._actors,
            'genres': self._genres,
            'vote_average': self._vote_average,
            'ratings': self._ratings,
            'runtime': self._runtime,
            'globalRating': self._globalRating
        }


class TVShow(Cinema):
    _collection = 'tvshows'

    def __init__(self, name, **kwargs):
        Cinema.__init__(self, name, **kwargs)
        self._seasons = kwargs.get('seasons', [])
        self._episodeLength = kwargs.get('episodeLength', '')

    @property
    def json(self):
        return {
            'name': self._name,
            'overview': self._overview,
            'homepage': self._homepage,
            'id': self._id,
            'mongo_id': str(self._mongo_id),
            'poster_path': self._poster_path,
            'release_date': self._release_date,
            'makers': self._makers,
            'producers': self._producers,
            'actors': self._actors,
            'genres': self._genres,
            'globalRating': self._globalRating,
            'ratings': self._ratings,
            'seasons': self._seasons,
        }

    def _addSeasonToDB(self, season):
        # update seasons current state in database
        instance_from_db = self
        if not self._mongo_id:
            instance_from_db = TVShow.get(name=self._name)
        else :
            instance_from_db = TVShow.get(_id=self._mongo_id)
        self._mongo_id = instance_from_db._mongo_id
        self._seasons = instance_from_db._seasons
        # add season
        self._seasons.append(season.json)
        # determine episode length
        self._episodeLength = mean(episode['runtime'] for s in self._seasons for episode in s['episodes'])
        # save in database
        if self._mongo_id:
            return TVShow.update_one({'_id': self._mongo_id}, {'$addToSet': {'seasons': season.json}, '$set': {'episodeLength': self._episodeLength}})

    def _addEpisodeToDB(self, episode, season):
        # update seasons current state in database
        instance_from_db = self
        if not self._mongo_id:
            instance_from_db = TVShow.get(name=self._name)
        else :
            instance_from_db = TVShow.get(_id=self._mongo_id)
        self._mongo_id = instance_from_db._mongo_id
        self._seasons = instance_from_db._seasons
        # update this season episodes with database state
        season._episodes = self._seasons[season._number-1]['episodes']
        # add episode
        season._episodes.append(episode.json)
        self._seasons[season._number-1] = season.json
        # determine episode length
        self._episodeLength = mean(episode['runtime'] for episode in season['episode'] for season in self._seasons)
        # save in database
        if self._mongo_id:
            return TVShow.update_one({'_id': self._mongo_id, 'seasons.number': season._number}, {'$addToSet': {'seasons.$.episodes': episode.json}, '$set': {'episodeLength': self._episodeLength}})


class Season:
    def __init__(self, name, number, tvShow, **kwargs):
        self._name = name
        self._overview = kwargs.get('overview', '')
        self._homepage = kwargs.get('homepage', '')
        self._poster_path = kwargs.get('poster_path', '')
        self._release_date = kwargs.get('release_date', None)
        self._makers = kwargs.get('makers', [])
        self._producers = kwargs.get('producers', [])
        self._actors = kwargs.get('actors', [])
        self._genres = kwargs.get('genres', [])
        self._number = number
        self._episodes = kwargs.get('episodes', [])
        self._tvShow = tvShow

    def _addEpisode(self, episode):
        self._episodes.append(episode.json)

    @property
    def json(self):
        return {
            'name': self._name,
            'overview': self._overview,
            'homepage': self._homepage,
            'poster_path': self._poster_path,
            'release_date': self._release_date,
            'makers': self._makers,
            'producers': self._producers,
            'actors': self._actors,
            'genres': self._genres,
            'number': self._number,
            'episodes': self._episodes,
        }


class Episode:
    def __init__(self, name, number, season, **kwargs):
        self._name = name
        self._overview = kwargs.get('overview', '')
        self._homepage = kwargs.get('homepage', '')
        self._poster_path = kwargs.get('poster_path', '')
        self._release_date = kwargs.get('release_date', None)
        self._makers = kwargs.get('makers', [])
        self._producers = kwargs.get('producers', [])
        self._actors = kwargs.get('actors', [])
        self._genres = kwargs.get('genres', [])
        self._number = number
        self._runtime = kwargs.get('runtime', 0)
        self._season = season
        self._tvShow = season._tvShow

    @property
    def json(self):
        return {
            'name': self._name,
            'overview': self._overview,
            'homepage': self._homepage,
            'poster_path': self._poster_path,
            'release_date': self._release_date,
            'makers': self._makers,
            'producers': self._producers,
            'actors': self._actors,
            'genres': self._genres,
            'number': self._number,
            'runtime': self._runtime,
        }
