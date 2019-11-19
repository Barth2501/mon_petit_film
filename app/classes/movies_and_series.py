from .dao import DAO
from bson.objectid import ObjectId
from statistics import mean


class Cinema(DAO):
    _collection = 'cinema'

    def __init__(self, name, **kwargs):
        self._id = kwargs.get('id', None)
        self._mongo_id = ObjectId(kwargs.get('_id')) if kwargs.get('_id', None) else None
        self._name = name
        self._overview = kwargs.get('overview', '')
        self._homepage = kwargs.get('homepage', '')
        self._poster_path = kwargs.get('poster_path', '')
        self._release_date = kwargs.get('release_date', None)
        self._makers = kwargs.get('makers', [])
        self._producers = kwargs.get('producers', [])
        self._actors = kwargs.get('actors', [])
        self._genres = kwargs.get('genres', [])
        self._vote_average = kwargs.get('vote_average') if isinstance(kwargs.get('vote_average', None), int) else 0
        self._ratings = kwargs.get('ratings', [])
        self._vote_count = kwargs.get('vote_count', 0)
        self._globalRating = kwargs.get('globalRating', None)

    def _addRating(self, userId, rating):
        if not self._mongo_id:
            instance_from_db = type(self).get(name=self._name)
            if instance_from_db:
                self._mongo_id = instance_from_db._mongo_id
                self._ratings = instance_from_db._ratings
        newRating = {'user': userId, 'rating': rating}
        self._ratings.append(newRating)
        self._globalRating = mean(rating['rating'] for rating in self._ratings)
        alreadyExist = Cinema.get(id=self._id, ratings__user=userId)
        if alreadyExist:
            if self._mongo_id:
                return Cinema.update_one({'_id':self._mongo_id, 'ratings.user':userId},{'$set': {'ratings.$.rating':rating, 'globalRating': self._globalRating}})
        if self._mongo_id:
            return type(self).update_one({'_id': self._mongo_id}, {'$push': {'ratings': newRating}, '$set': {'globalRating': self._globalRating}})

    @property
    def name(self):
        return self._name


class Movie(Cinema):
    def __init__(self, name, runtime, **kwargs):
        Cinema.__init__(self, name, **kwargs)
        self._runtime = kwargs.get('runtime', '')

    @property
    def json(self):
        return {
            'type': 'movie',
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
    def __init__(self, name, **kwargs):
        super().__init__(self, name, **kwargs)
        self._seasons = []
        self._episodes = []
        self._episodeLength = None

    @property
    def json(self):
        return {
            'type': 'tvshow',
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
            'globalRating': self._globalRating,
            'ratings': self._ratings,
            'seasons': self._seasons,
            'episodes': self._episodes,
        }

    def _addSeason(self, season):
        if not self._mongo_id:
            instance_from_db = TVShow.get(name=self._name)
            if instance_from_db:
                self._mongo_id = instance_from_db._mongo_id
                self._seasons = instance_from_db._seasons
        newSeason = {'id': season._id, 'number': season._number, 'name': season._name}
        self._seasons.append(newSeason)
        if self._mongo_id:
            return TVShow.update_one({'_id': self._mongo_id}, {'$push': {'seasons': newSeason}})

    # def _addEpisode(self, episode):
    #     if not self._mongo_id:
    #         instance_from_db = TVShow.get(name=self._name)
    #         if instance_from_db:
    #             self._mongo_id = instance_from_db._mongo_id
    #             self._episodes = instance_from_db._episodes
    #     newEpisode = {'id': episode._id, 'number': episode._number, 'name': episode._name}
    #     self._episodes.append(newEpisode)
    #     if self._mongo_id:
    #         return TVShow.update_one({'_id': self._mongo_id}, {'$push': {'episodes': newEpisode}})


class Season(Cinema):
    def __init__(self, name, number, tvShow, **kwargs):
        super().__init__(self, name, **kwargs)
        self._tvShow = tvShow
        self._number = number
        self._episodes = []
        tvShow._addSeason(self.json)

    @property
    def json(self):
        return {
            'type': 'season',
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
            'globalRating': self._globalRating,
            'ratings': self._ratings,
            'number': self._number,
            'episodes': self._episodes,
        }

    def _addEpisode(self, episode):
        if not self._mongo_id:
            instance_from_db = Season.get(name=self._name)
            if instance_from_db:
                self._mongo_id = instance_from_db._mongo_id
                self._episodes = instance_from_db._episodes
        newEpisode = {'id': episode._id, 'number': episode._number, 'name': episode._name}
        self._episodes.append(newEpisode)
        if self._mongo_id:
            return Season.update_one({'_id': self._mongo_id}, {'$push': {'episodes': newEpisode}})


class Episode(Cinema):
    def __init__(self, name, number, runtime, season, **kwargs):
        super().__init__(self, name, **kwargs)
        self._season = season
        self._tvShow = season._tvShow
        self._number = number
        self._runtime = runtime
        season._tvShow._addEpisode(self.json)
        season._addEpisode(self.json)

    @property
    def json(self):
        return {
            'type': 'episode',
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
            'globalRating': self._globalRating,
            'ratings': self._ratings,
            'number': self._number,
            'runtime': self._runtime,
        }
