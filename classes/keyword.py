"""
Module work with Keywords
"""
import pymongo
import config

mongo = pymongo.MongoClient(
    config.mongoclient)


class Word:
    """
    This class represent only one word
    """
    def __init__(self, word):
        """Initialize word"""
        self.keyword = word['keyword']
        self.links = word['links']


class Keywords:
    """
    This class represent all Keywords in list
    """
    keywords = mongo.db.keywords

    def __init__(self):
        """
        Get all keywords from db
        """
        self.keywords = {}
        all_keywords = Keywords.keywords.find({})
        for keyword in all_keywords:
            self.keywords[keyword['keyword']] = Word(keyword)

    def _check(self, word):
        """
        Check if smb already use this word
        :param word: str
        :return: bool
        """
        return word in self.keywords

    def add(self, word):
        """
        Add word to db and class
        :param word: str
        :return: None
        """
        if not self._check(word):
            Keywords.keywords.insert({'keyword': word, 'links': {}})
            self.keywords[word] = Word(Keywords.keywords.find_one({'keyword': word}))

    def __getitem__(self, item):
        """
        Get word from keylist
        :param item: str
        :return: word
        """
        return self.keywords[item]
