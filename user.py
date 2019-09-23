from ratings import Ratings

class User:

    userId = 1
    likedList = []

    def __init__(self, username, emailAddress, password):
        self._username = username
        self._emailAddress = emailAddress
        self._userId = User.userId
        self._password = password
        self._likedList = User.likedList
        User.userId += 1

    @property
    def username(self):
        return self._username

    @property
    def emailAddress(self):
        return self._emailAddress

    def _donne_note(self, rating, globalId):
        note = Ratings(self._userId, globalId, rating)
        note.save()
    
    def _aime(self, globalId):
        self._likedList.append(globalId)