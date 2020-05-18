"""
Module work with Keywords
"""
import copy
import string
import config
from ukr_stemmer import UkrainianStemmer
from db_connect import mongo
import re
import datetime
from datetime import datetime, timedelta
import random


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
        self.links_data = {}
        self.links_data['twitter'] = word['links_twitter_data']
        self.links_data['telegram'] = word['links_telegram_data']
        try:
            self.telegram_info = word['telegram_info']
        except KeyError:
            self.telegram_info = []
        try:
            self.twitter_info = word['twitter_info']
        except KeyError:
            self.twitter_info = []
        self.links_dict = {}
        self.twitter_replies = 0
        self.twitter_likes = 0
        self.twitter_retweets = 0
        self.telegram_views = 0
        self.telegram_reaction = 0
        self.telegram_posts = 0
        self.twitter_posts = 0

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
        if weight != 0:
            if source == 'telegram':
                self.telegram_reaction += info[0]
                try:
                    self.telegram_views += int(info[1])
                except:
                    self.telegram_views += int(info[1].split('.')[0]) * 1000
                self.telegram_posts += 1
            elif source == 'twitter':
                self.twitter_posts += 1
                self.twitter_likes += int(info[0])
                try:
                    self.twitter_retweets += int(info[1])
                except:
                    self.twitter_retweets += int(info[1].split('.')[0]) * 1000
                self.twitter_replies += int(info[2])

        to_add = True
        for now_link in range(len(self.links[source])):
            now_weight = self.links[source][now_link][0]
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

    @staticmethod
    def get_more_data(data):
        data = [int(x) for x in data]
        while len(data) != 7:
            data.append(0)
        return data

    @staticmethod
    def get_telegram_link_dict(link):
        data = [0] * 4
        data[0] = link[1]
        data[1] = link[2][:297]
        if len(link[2]) > 297:
            data[1] += '...'
        data[2] = link[3][0]
        data[3] = link[3][1]
        return data

    @staticmethod
    def get_twitter_link_dict(link):
        data = [0] * 6
        data[0] = link[1]
        data[1] = link[2][:297]
        if len(link[2]) > 297:
            data[1] += '...'
        data[2] = link[3][0]
        data[3] = link[3][1]
        data[4] = link[3][2]
        return data

    def transform(self, data):
        word = UkrainianStemmer(self.keyword).stem_word().lower()
        main_text = copy.copy(data[1]).split(' ')
        data[1] = [UkrainianStemmer(x).stem_word().lower() for x in data[1].split(' ')]
        data[1] = [x.translate(str.maketrans('', '', string.punctuation)) for x in data[1]]
        for i in range(len(data[1])):
            if data[1][i] == word:
                main_text[i] = '<b style="font-weight:750">{}</b>'.format(main_text[i])
        data[1] = ' '.join(main_text)
        return data

    def get_info(self):
        data = {}
        if len(self.telegram_info) == 0:
            return data
        data['telegram_views'] = self.get_more_data([x['telegram_views'] for x in self.telegram_info[:7]])
        data['telegram_reaction'] = self.get_more_data([x['telegram_reaction'] for x in self.telegram_info[:7]])
        data['telegram_posts'] = self.get_more_data([x['telegram_posts'] for x in self.telegram_info[:7]])
        data['twitter_replies'] = self.get_more_data([x['twitter_replies'] for x in self.twitter_info[:7]])
        data['twitter_likes'] = self.get_more_data([x['twitter_likes'] for x in self.twitter_info[:7]])
        data['twitter_retweets'] = self.get_more_data([x['twitter_retweets'] for x in self.twitter_info[:7]])
        data['twitter_posts'] = self.get_more_data([x['twitter_posts'] for x in self.twitter_info[:7]])
        data['telegram_links'] = [self.transform(self.get_telegram_link_dict(x)) for x in self.links_data['telegram']]
        data['twitter_links'] = [self.transform(self.get_twitter_link_dict(x)) for x in self.links_data['twitter']]
        return data

    def __str__(self):
        """
        String representation of a word.
        :return: str
        """
        return "%s" % (self.keyword)


class Keywords:
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
                                      'links_telegram': [], 'telegram_info': [], 'twitter_info': []})
            self.keywords[word] = Word({'keyword': word, 'links_twitter': [],
                                        'links_telegram': [], 'telegram_info': [], 'twitter_info': [],
                                        'telegram_views': 0, 'telegram_reaction': 0, 'telegram_posts': 0,
                                        'twitter_replies': 0, 'twitter_likes': 0, 'twitter_retweets': 0,
                                        'twitter_posts': 0})

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

    def push_changes(self, source):
        for word in self.keywords:
            word = self.keywords[word]
            telegram_info = word.telegram_info
            twitter_info = word.twitter_info
            if source == 'telegram':
                telegram_info.insert(0, {
                    'data': str(datetime.today())[:10],
                    'telegram_views': word.telegram_views,
                    'telegram_reaction': word.telegram_reaction,
                    'telegram_posts': word.telegram_posts})
                mongo.db.keywords.update({"keyword": word.keyword}, {"$set": {"links_telegram": word.links['telegram'],
                                                                              'telegram_info': telegram_info}})
            else:
                twitter_info.insert(0, {
                    'data': str(datetime.today())[:10],
                    'twitter_posts': word.twitter_posts,
                    'twitter_replies': word.twitter_replies,
                    'twitter_likes': word.twitter_likes,
                    'twitter_retweets': word.twitter_retweets})

                mongo.db.keywords.update({"keyword": word.keyword}, {"$set": {"links_twitter": word.links['twitter'],
                                                                              'twitter_info': twitter_info}})

    def clean_changes(self, source):
        for word in self.keywords:
            word = self.keywords[word]
            mongo.db.keywords.update({"keyword": word.keyword}, {"$set": {"links_telegram": [], 'links_twitter': [],
                                                                          "links_telegram_data": word.links['telegram'][
                                                                                                 :5],
                                                                          "links_twitter_data": word.links['twitter'][
                                                                                                :5]
                                                                          }})
        self.keywords = {}
        all_keywords = mongo.db.keywords.find({})
        for keyword in all_keywords:
            self.keywords[keyword['keyword']] = Word(keyword)
