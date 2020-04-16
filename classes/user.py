"""
 This module used to work with user
"""
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
    return User(session_name)


class User:
    """
    Class to work with user easier
    """
    keywords = Keywords()

    def __init__(self, username):
        """Initialize User"""
        users = mongo.db.users
        login_user = users.find_one({'name': username})
        self.username = login_user['name']
        self.password = login_user['password']
        self.keywords = login_user['keywords']
        self.email = login_user['email']

    def add_keyword(self, new_word):
        """Add keyword to user"""

        self.keywords.append(new_word)
        User.keywords.add(new_word)

        mongo.db.users.update({"name": self.username}, {"$set": {"keywords": self.keywords}})

    def to_save(self):
        """Return user in json format"""
        return {'name': self.username, 'password': self.password,
                'keywords': self.keywords, 'email': self.email}
