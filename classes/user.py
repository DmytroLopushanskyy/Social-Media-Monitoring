"""
 This module used to work with user
"""
import config
from db_connect import mongo
from classes.keyword import Keywords


class User:
    """
    Class to work with user easier
    """

    def __init__(self, username):
        """Initialize User"""
        users = mongo.db.users
        login_user = users.find_one({'name': username})
        if login_user is None:
            raise NameError("wrong username")
        self.username = login_user['name']
        self.password = login_user['password']
        self.keywords = login_user['keywords']
        self.email = login_user['email']
        self.weights = {'telegram': [], 'twitter': []}
        self.dict_weights = {}

    def add_keyword(self, new_word):
        """Add keyword to user"""

        self.keywords.append(new_word)
        words = Keywords()
        words.add(new_word)
        mongo.db.users.update({"name": self.username},
                              {"$set": {"keywords": self.keywords}})

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
        words = Keywords()
        for keyword in self.keywords:
            keyword = words.keywords[keyword]
            if link in keyword.links_dict:
                user_weight += keyword.links_dict[link]
        return user_weight

    def check_user_weight(self):
        """
        Sort weight of the user links to get most popular
        :param link: str
        :return:
        """
        for source in ['telegram', 'twitter']:
            new_links = []
            words = Keywords()
            for now in range(config.NUMBER_WORDS):

                dct = {}
                dct1 = {}
                for link in self.keywords:
                    link = words[link]
                    try:
                        dct[link.links[source][now][1]] = dct.get(link.links[source][now][0], 0) + 1
                        dct1[link.links[source][now][1]] = link.links[source][now]
                    except IndexError:
                        pass
                maxi = 0
                max_link = ''
                for i in dct:
                    try:
                        if dct[i] > maxi and i not in [x[1] for x in new_links]:
                            maxi = dct[i]
                            max_link = dct1[i]
                    except:
                        pass
                new_links.append(max_link)
            self.weights[source] = new_links

    def update_links(self, source):
        """
        Push changes
        :return:
        """
        self.check_user_weight()
        for x in range(len(self.weights[source])):
            try:
                self.weights[source][x][1] = self.weights[source][x][1].replace('\n', '')
            except IndexError:
                pass
        mongo.db.users.update({"name": self.username},
                              {"$set": {"links_" + source: self.weights[source]}})

    def get_links(self, source):
        """
        Get user links
        :return: list of links
        """
        return mongo.db.users.find_one({"name": self.username})['links_' + source]

    def get_full_data(self):
        to_return = {}
        keywords = Keywords()
        for word in self.keywords:
            to_return[word] = keywords[word].get_info()
        return to_return

    def get_pretty_links(self, source):
        data = self.get_links(source)
        to_return = []
        for x in data:
            if x == '':
                continue
            if len(x[2]) > 300:
                x[2] = x[2][:297] + '...'
            to_return.append([x[1], x[2], x[3][0], x[3][1]])
            if source == 'twitter':
                to_return[-1].append(x[3][2])
        return to_return



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
        users_name.append(User(user['name']))
    return users_name
