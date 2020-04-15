import pymongo
import config
from classes.keyword import Keywords

mongo = pymongo.MongoClient(
    config.mongoclient)


def to_class(session_name):
    """
    Create class from user
    :param session_name: name
    :return: None
    """
    return User(session_name['name'])


class User:
    keywords = Keywords()

    def __init__(self, username):
        """Initialize User"""
        users = mongo.db.users
        login_user = users.find_one({'name': username})
        self.username = login_user['name']
        self.password = login_user['password']
        self.keywords = login_user['keywords']

    def add_keyword(self, new_word):
        """Add keyword to user"""
        if new_word not in self.keywords:
            self.keywords.append(new_word)
            User.keywords.add(new_word)

            mongo.db.users.update({"name": self.username}, {"$set": {"keywords": self.keywords}})

        else:
            return 'You already have this word in your keyword list'

    def to_save(self):
        """Return user in json format"""
        return {'name': self.username, 'password': self.password, 'keywords': self.keywords}
