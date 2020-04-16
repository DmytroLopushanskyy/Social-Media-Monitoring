"""
Main parsing module.
"""
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from telegram_parsing.tg_parse import parse_telegram

SCHED = BlockingScheduler()

# GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google-chrome'
# CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

GOOGLE_CHROME_BIN = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'


class Parser:
    """
    Main Parser class.
    """
    def __init__(self):
        """
        Parser initialisation by launching the browser.
        """
        self.browser = browser_setup()
        self.tg_sources_path = 'telegram_parsing/channels.txt'

    def parse_telegram(self):
        """
        Launches telegram channels parsing.
        :return: None
        """
        parse_telegram(self)

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


def browser_setup():
    """
    Initial browser setup
    :return: Selenium WebDriver
    """
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')
    options.add_argument('--start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.binary_location = GOOGLE_CHROME_BIN
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                               chrome_options=options)
    browser.set_window_position(0, 0)
    browser.set_window_size(1110, 768)
    return browser


@SCHED.scheduled_job('interval', hours=24, next_run_time=datetime.now())
def start_parsing():
    """
    Main parsing starting function.
    :return: None
    """
    logging.info("Parsing process started!")
    main_parser = Parser()
    main_parser.parse_telegram()
    logging.info("Parsing process finished!")


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    SCHED.start()
