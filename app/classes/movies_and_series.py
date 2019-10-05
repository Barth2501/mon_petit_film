from app.database import DB
from app.classes.ratings import *

class Cinema(object):
    def __init__(self, name, **kwargs):
        self._name = name
        self._overview = kwargs.get('overview', '')
        self._homepage = kwargs.get('homepage','')
        self._id = kwargs.get('id',None)
        self._poster_path = kwargs.get('poster_path','')
        self._release_date = kwargs.get('release_date',None)
        self._makers = kwargs.get('makers', [])
        self._producers = kwargs.get('producers', [])
        self._actors = kwargs.get('actors', [])
        self._genres = kwargs.get('genres', 'Unknown')
        self._globalRating = kwargs.get('vote_average', 0)/2
        self._ratings = []
        
    def _addRating(self, user, rating):
        self._ratings.append({
            'user': user,
            'rating': rating
        })
        self._globalRating = sum(rating['rating'] for rating in self._ratings)
        DB.update_one(collection='cinema', 
            query={'name':self._name},
            new_values={
                '$set': {
                    'globalRating': self._globalRating,
                    'ratings': self._ratings
                }
            })

    @property
    def name(self):
        return self._name

class TVShow(Cinema):
    def __init__(self, name, **kwargs):
        Cinema.__init__(self, name, **kwargs)
        self._seasons = []
        self._episodes = []
        self._episodeLength = None
        if not DB.find_one(collection='cinema', query={'name': self._name}):
            DB.insert(collection= 'cinema', data=self.json)

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
            #'episodes': self._episodes,
        }

    def _addSeason(self, season):
        self._seasons.append(season)
        DB.update_one(collection='cinema', query={
            'name': self._name,
        }, new_values={
            '$set': {'seasons': self._seasons}
        })

    # def _addEpisode(self, episode):
    #     self._episodes.append(episode)
    #     DB.update_one(collection='cinema', query={
    #         'name': self._name,
    #     }, new_values={
    #         '$set': {'episodes': self._episodes}
    #     })

class Movie(Cinema):
    def __init__(self, name, runtime, **kwargs):
        Cinema.__init__(self, name, **kwargs)
        self._runtime = runtime
        if not DB.find_one(collection='cinema', query={'name': self._name}):
            DB.insert(collection='cinema', data=self.json)

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
            'globalRating': self._globalRating,
            'ratings': self._ratings,
            'runtime': self._runtime,
        }
class Season(Cinema):
    def __init__(self, name, number, tvShow, **kwargs):
        Cinema.__init__(self, name, **kwargs)
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
        self._episodes.append(episode)
        DB.update_one(collection='cinema', 
            query={'seasons.name': self._name}, 
            new_values=
                {'$set':
                    {'seasons.$.episodes': self._episodes}
                })

class Episode(Cinema):

    def __init__(self, name, number, runtime, season, **kwargs):
        Cinema.__init__(self, name, **kwargs)
        self._season = season
        self._tvShow = season._tvShow
        self._number = number
        self._runtime = runtime
        #season._tvShow._addEpisode(self.json)
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