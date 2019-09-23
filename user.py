class User:
    def __init__(self, username, emailAddress, password):
        self._username = username
        self._emailAddress = emailAddress
        self._password = password
        self._ratings = []

    def _addRating(self, rating):
        self._ratings.append(rating)
