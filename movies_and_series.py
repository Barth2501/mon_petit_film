class Genre:

    globalId = 1

    def __init__(self,name):
        self._name = name
        self._globalId = Genre.globalId
        Genre.globalId += 1

    @property
    def name(self):
        return self._name


class Serie(Genre):

    serieId = 1

    def __init__(self, title, overview, homepage, nbSeason, genre):
        Genre.__init__(self, genre)
        self._title = title
        self._overview = overview
        self._homepage = homepage
        self._nbSeason = nbSeason
        self._serieId = Serie.serieId

    @property
    def title(self):
        return self._title

    @property
    def overview(self):
        return self._overview
    
    @property
    def homepage(self):
        return self._homepage
    
    @property
    def nbSeason(self):
        return self._nbSeason

class Season(Serie):

    seasonId = 1

    def __init__(self, title, overview, homepage, nbSeason, genre, seasonTitle, seasonOverview, nbEpisode):
        Serie.__init__(self, title, overview, homepage, nbSeason, genre)
        self._seasonTitle = seasonTitle
        self._seasonOverview = seasonOverview
        self._nbEpisode = nbEpisode

    @property
    def seasonTitle(self):
        return self._seasonTitle

    @property
    def seasonOverview(self):
        return self._seasonOverview

    @property
    def nbEpisode(self):
        return self._nbEpisode

class Episode(Season):

    episodeId = 1

    def __init__(self, title, overview, homepage, nbSeason, genre, seasonTitle, seasonOverview, nbEpisode, episodeTitle, runningTime):
        Season.__init__(self, title, overview, homepage, nbSeason, genre, seasonTitle, seasonOverview, nbEpisode)
        self._episodeTitle = episodeTitle
        self._runningTime = runningTime
        self._episodeId = Episode.episodeId
        Episode.episodeId += 1 

    @property
    def episodeTitle(self):
        return self._episodeTitle

    @property
    def runningtime(self):
        return self._runningTime

class Movie(Episode):

    movieId = 1

    def __init__(self, title, runTime, overview, homePage, genre, runningTime):
        Episode.__init__(self, title, overview, 1, homePage, genre, title, overview, 1, title, runningTime)
        self._movieId = Movie.movieId
        Movie.movieId += 1
