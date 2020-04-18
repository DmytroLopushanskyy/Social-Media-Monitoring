"""
 This module used to work with user
"""
import pymongo
import config
from classes.keyword import words

mongo = pymongo.MongoClient(
    config.mongoclient)


class User:
    """
    Class to work with user easier
    """

    def __init__(self, username):
        """Initialize User"""
        users = mongo.db.users
        login_user = users.find_one({'name': username})
        self.username = login_user['name']
        self.password = login_user['password']
        self.keywords = login_user['keywords']
        self.email = login_user['email']
        self.weights = []
        self.dict_weights = {}

    def add_keyword(self, new_word):
        """Add keyword to user"""

        self.keywords.append(new_word)
        words.add(new_word)

        mongo.db.users.update({"name": self.username}, {"$set": {"keywords": self.keywords}})

    def to_save(self):
        """Return user in json format"""
        return {'name': self.username, 'password': self.password,
                'keywords': self.keywords, 'email': self.email}

    def get_user_weight(self, link):
        """
        Get weight of the link for special user
        :param link: str
        :return: int
        """
        user_weight = 0
        for keyword in self.keywords:
            keyword = words.keywords[keyword]
            if link in keyword.links_dict:
                user_weight += keyword.links_dict[link]
        return user_weight

    def check_user_weight(self, link):
        """
        Sort weight of the user links to get most popular
        :param link: str
        :return:
        """
        weight = self.get_user_weight(link)
        to_add = True
        for now_link in range(len(self.weights)):
            now_weight = self.weights[now_link][0]
            if weight > now_weight:
                self.weights.insert(now_link, (weight, link))
                to_add = False
                break
        if len(self.weights) < config.NUMBER_WORDS and to_add:
            self.weights.append((weight, link))

        if len(self.weights) > config.NUMBER_WORDS:
            self.weights.pop()

    def update_links(self):
        """
        Push changes
        :return:
        """
        print(self.weights)
        mongo.db.users.update({"name": self.username}, {"$set": {"links": [x[1] for x in self.weights]}})

    def get_links(self):
        """
        Get user links
        :return: list of links
        """
        return mongo.db.users.find_one({"name": self.username})['links']


def to_class(session_name):
    """
    Create class from user
    :param session_name: name
    :return: None
    """
    return User(session_name)


def get_all_users():
    """
    Get all users
    :return: list of User
    """
    users = mongo.db.users
    users = users.find({})
    users_name = []
    for user in users:
        print(user)
        users_name.append(User(user['name']))
    return users_name
