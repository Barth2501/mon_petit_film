from app.database import DB
from flask_login import UserMixin


class User(UserMixin, object):
    __tablename__ = 'user'

    def __init__(self, username, emailAddress, password):
        self._username = username
        self._emailAddress = emailAddress
        self._password = password
        self._ratings = []
        if not DB.find_one('user', {'username':self._username}):
            DB.insert(collection='user', data=self.json)

    @property
    def json(self):
        return {
            'username':self._username,
            'emailAddress':self._emailAddress,
            'password':self._password,
            'ratings':self._ratings,
        }

    @property
    def username(self):
        return self._username

    def _addRating(self, cinema, rating):
        self._ratings.append({
            'cinema': cinema,
            'rating': rating,
        })
        DB.update_one(collection='user', 
            query={'username': self._username},
            new_values={'$set': {'ratings': self._ratings}
        })

@login.user_loader
def load_user(id):
    return User.query.get(int(id))