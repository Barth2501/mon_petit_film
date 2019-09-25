class Cinema:
    def __init__(self, name, **kwargs):
        self._name = name
        self._overview = kwargs.get('overview', '')
        self._makers = kwargs.get('makers', [])
        self._producers = kwargs.get('producers', [])
        self._actors = kwargs.get('actors', [])
        self._type = kwargs.get('type', 'Unknown')
        self._globalRating = None
        self._ratings = []

    def _addRating(self, newRating):
        self._ratings.append(newRating)
        self._globalRating = sum(rating._rating for rating in self._ratings)


class TVShow(Cinema):
    def __init__(self, name, **kwargs):
        super().__init__(self, name, **kwargs)
        self._seasons = []
        self._episodes = []
        self._episodeLength = None

    def _addSeason(self, season):
        self._seasons.append(season)

    def _addEpisode(self, episode):
        self._episodes.append(episode)


class Movie(Cinema):
    def __init__(self, name, length, **kwargs):
        super().__init__(self, name, **kwargs)
        self._length = length


class Season(Cinema):
    def __init__(self, name, number, tvShow, **kwargs):
        super().__init__(self, name, **kwargs)
        self._tvShow = tvShow
        tvShow._addSeason(self)
        self._number = number
        self._episodes = []

    def _addEpisode(self, episode):
        self._episodes.append(episode)


class Episode(Cinema):
    def __init__(self, name, number, length, season, **kwargs):
        super().__init__(self, name, **kwargs)
        self._season = season
        season._addEpisode(self)
        self._tvShow = season._tvShow
        season._tvShow._addEpisode(self)
        self._number = number
        self._length = length
