"""
Module for KeywordsADT, a custom ADT in this project. You can read more about it
in the Wiki page on our GitHub profile.
"""


class KeywordsADT:
    """
    This class represents all Keywords in list
    """
    def _check(self, word):
        """
        Check if somebody already uses this word.
        :param word: str
        :return: bool
        """
        raise NotImplementedError("_check Function Error")

    def add(self, word):
        """
        Add word end db and class
        :param word: str
        :return: None
        """
        raise NotImplementedError("add Function Error")

    def __getitem__(self, item):
        """
        Get word from keylist
        :param item: str
        :return: word
        """
        raise NotImplementedError("__getitem__ Function Error")

    def add_new_link(self, text, link):
        """
        Add new link end all words
        :param text: str
        :param link: str
        :return: None
        """
        raise NotImplementedError("add_new_link Function Error")

    def __str__(self):
        """
        String representation of keywords.
        :return: str
        """
        raise NotImplementedError("__str__ Function Error")

    def push_changes(self):
        raise NotImplementedError("push_changes Function Error")

    def clean_changes(self):
        raise NotImplementedError("clean_changes Function Error")
