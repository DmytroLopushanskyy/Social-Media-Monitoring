"""
Module work with Keywords
"""
import string
import re
import config
from ukr_stemmer import UkrainianStemmer
from db_connect import mongo
from classes.KeywordsADT import KeywordsADT


def ukrainian(word):
    for letter in word:
        if re.search('[\u0400-\u04FF]', letter):
            continue
        return False
    return True


class Word:
    """
    This class represent only one word
    """

    def __init__(self, word):
        """Initialize word"""
        self.keyword = word['keyword']
        self.links = {}
        self.links['twitter'] = word['links_twitter']
        self.links['telegram'] = word['links_telegram']
        self.days_info = word['days_info']
        self.links_dict = {}

    def find_weight(self, text):
        """
        Find weight of a word in text
        :param text: str
        :return: int
        """
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = [UkrainianStemmer(x).stem_word().lower() for x in text.split()]
        weight = text.count(UkrainianStemmer(self.keyword).stem_word().lower())
        return weight

    def check_link(self, text, link, source, info):
        """
        Get weight of the link and add it if needed
        :param text: str
        :param link: str
        :return: None
        """
        weight = self.find_weight(text)
        print("weight", weight)
        to_add = True
        for now_link in range(len(self.links[source])):
            now_weight = self.links[source][now_link][0]
            print(weight, now_weight)
            if weight > now_weight:
                self.links[source].insert(now_link, (weight, link, text, info))
                to_add = False
                break
        if len(self.links[source]) < config.NUMBER_WORDS and to_add and weight > 0:
            print("added!")
            self.links[source].append((weight, link, text, info))

        if len(self.links[source]) > config.NUMBER_WORDS:
            self.links[source].pop()

    def transform_to_dict(self):
        """
        Transform links and weight to dict for faster work
        :return: None
        """
        for now in self.links:
            self.links_dict[now[1]] = now

    def __str__(self):
        """
        String representation of a word.
        :return: str
        """
        return "%s: %s" % (self.keyword, self.links_dict[0])


class Keywords(KeywordsADT):
    """
    This class represent all Keywords in list
    """

    def __init__(self):
        """
        Get all keywords from db
        """
        self.keywords = {}
        all_keywords = mongo.db.keywords.find({})
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
        if not mongo.db.keywords.find_one({'keyword': word}):
            mongo.db.keywords.insert({'keyword': word, 'links_twitter': [],
                                      'links_telegram': [], 'days_info': []})
            self.keywords[word] = Word({'keyword': word, 'links_twitter': [],
                                        'links_telegram': [], 'days_info': []})

    def __getitem__(self, item):
        """
        Get word from keylist
        :param item: str
        :return: word
        """
        return self.keywords[item]

    def add_new_link(self, text, link, source, info):
        """
        Add new link to all words
        :param text: str
        :param link: str
        :return: None
        """
        print("Adding new link")
        for word in self.keywords:
            word = self.keywords[word]
            word.check_link(text, link, source, info)
            word.transform_to_dict()

    def __str__(self):
        """
        String representation of keywords.
        :return: str
        """
        output = ""
        for word in self.keywords:
            output += str(word) + "\n"
        return output

    def push_changes(self):
        for word in self.keywords:
            word = self.keywords[word]
            print([x[1] for x in word.links], word.keyword)
            mongo.db.keywords.update({"keyword": word.keyword}, {"$set": {"links_telegram": word.links['telegram'],
                                                                          'links_twitter': word.links['twitter']}})

    def clean_changes(self):
        for word in self.keywords:
            word = self.keywords[word]
            mongo.db.keywords.update({"keyword": word.keyword}, {"$set": {"links_telegram": [], 'links_twitter': []}})
        self.keywords = {}
        all_keywords = mongo.db.keywords.find({})
        for keyword in all_keywords:
            self.keywords[keyword['keyword']] = Word(keyword)
