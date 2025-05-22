from flask_login import UserMixin

users = {"admin": {"password": "securepass"}}  # You can change credentials

class User(UserMixin):
    def __init__(self, username):
        self.id = username

    @staticmethod
    def validate(username, password):
        user = users.get(username)
        return user and user["password"] == password
