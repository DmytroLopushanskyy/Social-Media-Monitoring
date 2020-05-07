"""
Main parsing module.
"""
import logging
import random
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from telegram_parsing.tg_parse import parse_telegram
from twitter_parsing.twitter_parse import parse_twitter
from classes.keyword import Keywords
#from classes.user import get_all_users

SCHED = BlockingScheduler()

# GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google-chrome'
# CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

GOOGLE_CHROME_BIN = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'

req_proxy = RequestProxy()
proxies = req_proxy.get_proxy_list()


class Parser:
    """
    Main Parser class.
    """
    def __init__(self, keywords):
        """
        Parser initialisation by launching the browser.
        """
        self.browser = self.browser_setup()
        self.tg_sources_path = 'telegram_parsing/channels.txt'
        self.keywords = keywords

    def parse_telegram(self):
        """
        Launches telegram channels parsing.
        :return: None
        """
        parse_telegram(self)
        
    def parse_twitter(self):
        """
        Launches telegram channels parsing.
        :return: None
        """
        keywords = self.get_user_keywords()
        parse_twitter(self, keywords)
        
    def get_user_keywords(self):
        """
        Gets all user keywords from the database
        :return: list of str
        """
        return ["coronavirus", "коронавірус", "україна", "трамп"]

    @staticmethod
    def by_class(search_in, class_name, get_text=False):
        """
        Search for an element by its class_name.
        :param search_in: Selenium WebElement
        :param class_name: str
        :param get_text: bool
        :return: Selenium WebElement or None if not found
        """
        result = None
        try:
            result = search_in.find_element_by_class_name(class_name)
            if result and get_text:
                result = result.text
        except NoSuchElementException:
            pass

        return result

    def quit(self):
        """
        Quit parsing by safely closing and quitting the browser.
        :return:
        """
        self.browser.close()
        self.browser.quit()

    def new_link(self, text, link):
        """
        This function get information about post, and
        update weights of keywords and user to get most popular one
        :param text: str
        :param link: str
        :return: None
        """
        self.keywords.add_new_link(text, link)

    @staticmethod
    def browser_setup(iter=0, update_proxies=False):
        """
        Initial browser setup
        :param update_proxies: bool
        :param iter: int
        :return: Selenium WebDriver
        """
        global proxies
        if update_proxies:
            proxies = RequestProxy().get_proxy_list()
        chosen_proxy = proxies[iter]
        logging.info("Chosen Proxy: %s" % chosen_proxy)
        PROXY = chosen_proxy.get_address()
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
            "sslProxy": PROXY,
            "proxyType": "MANUAL",
        }

        options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--headless')
        options.add_argument('--start-maximized')
        options.add_argument('disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument("user-agent=Chrome/80.0.3800.23")
        options.add_argument('--no-sandbox')
        options.binary_location = GOOGLE_CHROME_BIN
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                                   chrome_options=options)
        browser.set_window_position(0, 0)
        browser.set_window_size(320, 9999)
        # browser.header_overrides = {
        #     'user-agent': 'Mozilla/5.0',
        # }
        # browser._client.set_header_overrides(headers=dict_headers)
        return browser


def update():
    """
    This function push information into database
    :return: None
    """
    global users
    for user in users:
        user.check_user_weight()
        user.update_links()


@SCHED.scheduled_job('interval', hours=24, next_run_time=datetime.now())
def start_parsing(update_proxies=True):
    """
    Main parsing starting function.
    :return: None
    """
    logging.info("Retrieving all keywords from database")
    words = Keywords()
    #print(words)
    logging.info("Parsing process started!")
    main_parser = Parser(words)
    #main_parser.parse_telegram()
    main_parser.parse_twitter()
    logging.info("Parsing process finished!")
    #print(words)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    SCHED.start()
