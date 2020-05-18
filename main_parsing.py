"""
Main parsing module.
"""
import logging
import socket
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
from selenium.webdriver.remote.webdriver import WebDriver
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from telegram_parsing.tg_parse import parse_telegram
from twitter_parsing.twitter_parse import parse_twitter
from classes.keyword import Keywords
from classes.user import get_all_users
from config import GOOGLE_CHROME_BIN, CHROMEDRIVER_PATH, logger


def attach_to_session(executor_url, session_id, options, proxy):
    """
    Attach browser to session.
    """
    original_execute = WebDriver.execute

    def new_command_execute(self, command, params=None):
        """ Mock the response """
        if command == "newSession":

            return {'success': 0, 'value': None, 'sessionId': session_id}
        return original_execute(self, command, params)
    # Patch the function before creating the driver object
    WebDriver.execute = new_command_execute
    webdriver.DesiredCapabilities.CHROME['proxy'] = {
        "httpProxy": proxy,
        "ftpProxy": proxy,
        "sslProxy": proxy,
        "proxyType": "MANUAL",
    }
    driver = webdriver.Remote(command_executor=executor_url,
                              desired_capabilities={}, options=options)
    driver.session_id = session_id
    # Replace the patched function with original function
    WebDriver.execute = original_execute
    return driver


def is_bad_proxy(pip):
    """
    Simple prxoy validation.
    :param pip: str
    :return: bool
    """
    try:
        proxy_handler = urllib.request.ProxyHandler({'http': pip})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        req = urllib.request.Request('http://www.google.com')
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as error:
        print('Error code: ', error.code)
        return error.code
    except Exception as detail:
        print("ERROR:", detail)
        return True
    return False


SCHED = BlockingScheduler()

req_proxy = RequestProxy()
proxies = req_proxy.get_proxy_list()
next_run = datetime.now() + timedelta(hours=3)

selenium_logger.setLevel(logging.WARNING)


class Parser:
    """
    Main Parser class.
    """

    def __init__(self, use_proxy=False):
        """
        Parser initialisation by launching the browser.
        """
        self.browser = self.browser_setup(use_proxy=use_proxy)
        self.tg_sources_path = 'telegram_parsing/channels.txt'
        self.keywords = Keywords()

    def parse_telegram(self):
        """
        Launches telegram channels parsing.
        :return: None
        """
        parse_telegram(self)

    def parse_twitter(self):
        """
        Launches telegram channels parsing.
        :param keywords: list
        :return: None
        """
        parse_twitter(self)

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

    def new_link(self, text, link, source, info):
        """
        This function get information about post, and
        update weights of keywords and user to get most popular one
        :param text: str
        :param link: str
        :return: None
        """
        self.keywords.add_new_link(text, link, source, info)

    def browser_setup(self, iter=0, update_proxies=False, use_proxy=True):
        """
        Initial browser setup
        :param update_proxies: bool
        :param iter: int
        :return: Selenium WebDriver
        """
        global proxies, req_proxy

        if update_proxies:
            req_proxy.__init__()
            proxies = req_proxy.get_proxy_list()

        if use_proxy:
            socket.setdefaulttimeout(120)

            for current_proxy in proxies:
                proxy = proxies[iter].get_address()
                if not is_bad_proxy(proxy):
                    logger.info("Chosen Proxy: %s", proxy)
                    webdriver.DesiredCapabilities.CHROME['proxy'] = {
                        "httpProxy": proxy,
                        "ftpProxy": proxy,
                        "sslProxy": proxy,
                        "proxyType": "MANUAL",
                    }
                    break
                print("%s is a BAD PROXY" % (current_proxy))
        else:
            proxy = None


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

        if hasattr(self, 'browser'):
            executor_url = self.browser.command_executor._url
            session_id = self.browser.session_id
            browser = attach_to_session(executor_url, session_id, options, proxy)
            from twitter_parsing.twitter_parse import send
            send("browser succesfully attached to session!")
        else:
            browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                                       chrome_options=options)
        # logger.info("Reloading capabilities")
        # browser.desired_capabilities.update(options.to_capabilities())

        #browser.set_window_position(0, 0)
        #browser.set_window_size(320, 9999)
        # browser.header_overrides = {
        #     'user-agent': 'Mozilla/5.0',
        # }
        # browser._client.set_header_overrides(headers=dict_headers)
        return browser


def update(source):
    """
    This function push information into database
    :return: None
    """
    global users
    for user in users:
        user.check_user_weight()
        user.update_links(source)


@SCHED.scheduled_job('interval', hours=24, next_run_time=datetime.now())
def start_parsing():
    """
    Main parsing starting function.
    :return: None
    """
    logger.info("Parsing process started!")
    main_parser = Parser()
    main_parser.parse_telegram()
    # main_parser.parse_twitter()
    logging.info("Parsing process finished!")
    main_parser.keywords.push_changes('telegram')
    users = get_all_users()
    for user in users:
        user.update_links('telegram')
    main_parser.keywords.clean_changes('telegram')
    print('SUCCESS!')


@SCHED.scheduled_job('interval', hours=24, next_run_time=next_run)
def start_twitter_parsing():
    """
    Main parsing starting function.
    :return: None
    """
    logger.info("Parsing process started!")
    main_parser = Parser(use_proxy=True)
    main_parser.parse_twitter()
    logging.info("Parsing process finished!")
    main_parser.keywords.push_changes('twitter')
    users = get_all_users()
    for user in users:
        user.update_links('twitter')
    main_parser.keywords.clean_changes('twitter')
    print('SUCCESS!')


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    SCHED.start()
