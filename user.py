from .ratings import Ratings

class User():

    userId = 1
    liked_list = []

    def __init__(self, username, emailAdress, password):
        self._username = username
        self._emailAdress = emailAdress
        self._userId = User.userId
        self._password = password
        self._liked_list = User.liked_list
        User.userId += 1

    @property
    def username(self):
        return self._username

    @property
    def emailAdress(self):
        return self._emailAdress

    def _donne_note(self,rating, globalId):
        note = Ratings(self._userId,globalId, rating)
        note.save()
    
    def _aime(self,globalId):
        self._liked_list.append(globalId)