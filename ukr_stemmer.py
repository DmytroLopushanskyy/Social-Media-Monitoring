"""
This code is already uploaded in Github:
https://github.com/Amice13/ukr_stemmer



Russian stemming algorithm provided by Dr Martin Porter (snowball.tartarus.org):
http://snowball.tartarus.org/algorithms/russian/stemmer.html
Algorithm implementation in PHP provided by Dmitry Koterov (dklab.ru):
http://forum.dklab.ru/php/advises/HeuristicWithoutTheDictionaryExtractionOfARootFromRussianWord.html
Algorithm implementation adopted for Drupal by Algenon (4algenon@gmail.com):
https://drupal.org/project/ukstemmer
Algorithm implementation in Python by Zakharov Kyrylo
https://github.com/Amice13
"""

import re


class UkrainianStemmer():
    """
    Class to get origin of the word
    """

    def __init__(self, word):
        """
        Initialize word
        :param word: str
        """
        self.word = word
        self.vowel = r'аеиоуюяіїє'  # http://uk.wikipedia.org/wiki/Голосний_звук
        self.perfectiveground = r'(ив|ивши|ившись|ыв|ывши|ывшись((?<=[ая])(в|вши|вшись)))$'
        # http://uk.wikipedia.org/wiki/Рефлексивне_дієслово
        self.reflexive = r'(с[яьи])$'
        # http://uk.wikipedia.org/wiki/Прикметник + http://wapedia.mobi/uk/Прикметник
        self.adjective = r'(ими|ій|ий|а|е|ова|ове|ів|є|їй|єє|еє|я|ім|ем|им|ім|их|' \
                         r'іх|ою|йми|іми|у|ю|ого|ому|ої|на|ний|но)$'
        # http://uk.wikipedia.org/wiki/Дієприкметник
        self.participle = r'(ий|ого|ому|им|ім|а|ій|у|ою|ій|і|их|йми|их)$'
        # http://uk.wikipedia.org/wiki/Дієслово
        self.verb = r'(сь|ся|ив|ать|ять|у|ю|ав|али|учи|ячи|вши|ши|е|ме|ати|яти|є)$'
        # http://uk.wikipedia.org/wiki/Іменник
        self.noun = r'(а|ев|ов|е|ями|ами|еи|и|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у' \
                    r'|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я|і|ові|ї|ею|єю|ою|є|еві|ем|єм|ів|їв|ю)$'
        self.rvre = r'[аеиоуюяіїє]'
        self.derivational = r'[^аеиоуюяіїє][аеиоуюяіїє]+[^аеиоуюяіїє]+[аеиоуюяіїє].*(?<=о)сть?$'
        self.reverse = ''

    @staticmethod
    def ukstemmer_search_preprocess(word):
        """
        Change russian symbols end ukrainian
        :param word:
        :return:
        """
        word = word.lower()
        word = word.replace("'", "")
        word = word.replace("ё", "е")
        word = word.replace("ъ", "ї")
        return word

    def str_check(self, start, reg, end):
        """
        Check string
        :param start: str
        :param reg: int
        :param end: int
        :return:
        """
        orig = start
        self.reverse = re.sub(reg, end, start)
        return orig != self.reverse

    def stem_word(self):
        """
        Get the origin of ukrainian word
        :return: str
        """
        word = self.ukstemmer_search_preprocess(self.word)
        if not re.search('[аеиоуюяіїє]', word):
            stem = word
        else:
            str_p = re.search(self.rvre, word)
            start = word[0:str_p.span()[1]]
            self.reverse = word[str_p.span()[1]:]

            # Step 1
            if not self.str_check(self.reverse, self.perfectiveground, ''):

                self.str_check(self.reverse, self.reflexive, '')
                if self.str_check(self.reverse, self.adjective, ''):
                    self.str_check(self.reverse, self.participle, '')
                else:
                    if not self.str_check(self.reverse, self.verb, ''):
                        self.str_check(self.reverse, self.noun, '')
            # Step 2
            self.str_check(self.reverse, 'и$', '')

            # Step 3
            if re.search(self.derivational, self.reverse):
                self.str_check(self.reverse, 'ость$', '')

            # Step 4
            if self.str_check(self.reverse, 'ь$', ''):
                self.str_check(self.reverse, 'ейше?$', '')
                self.str_check(self.reverse, 'нн$', u'н')

            stem = start + self.reverse
        return stem
