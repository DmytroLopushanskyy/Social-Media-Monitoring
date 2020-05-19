"""
Telegram parsing module
"""
import re
import time
from datetime import datetime, timedelta
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from twitter_parsing.twitter_parse_bug import send
from config import logger

def parse_telegram(parser):
    """
    Main Telegram channels parsing function.
    :param parser: Parser
    :return: None
    """
    start = time.time()
    browser = parser.browser
    channels = get_channels(parser.tg_sources_path)

    to_parse = [get_date(datetime.now() - timedelta(days=1))]
    dates = [get_date(datetime.now())]
    logger.info("Starting parsing process. Dates: %s", dates)
    missed = set()
    got_text = 0

    for num, source in enumerate(channels):
        url = 'https://t.me/s/' + source[1:]

        response = requests.get(url)
        if not response.url.startswith('https://t.me/s/'):  # catch redirect
            logger.warning("Channel parsing not working!")
            continue

        browser.get(url)

        try:
            WebDriverWait(browser, 3).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, 'tgme_widget_message')))
        except TimeoutException:
            logger.error("Error while parsing! %s" % url)
            continue
        posts = browser.find_element_by_class_name('tgme_channel_history') \
            .find_elements_by_class_name('tgme_widget_message_wrap')
        posts.reverse()
        for post in posts:
            try:
                post_date = post.find_element_by_class_name('tgme_widget_message'
                                                            '_service_date_wrap')\
                    .find_element_by_class_name('tgme_widget_message_service_date')
            except:
                send("Error with url " + url)
                continue

            post_date = post_date.get_attribute('innerHTML')
            if post_date not in dates and post_date not in to_parse:
                break
            elif post_date in dates:
                continue

            post = post.find_element_by_class_name('tgme_widget_message')
            post_id = post.get_attribute('data-post').split('/')[1]

            link = parser.by_class(post, 'tgme_widget_message_link_preview')
            text = parser.by_class(post, 'tgme_widget_message_text', True)
            button_link = parser. \
                by_class(post, 'tgme_widget_message_inline_button')
            external_link_text = parser. \
                by_class(post, 'tgme_widget_message_inline_button_text', True, True)
            reactions = 0
            if external_link_text:

                for el in external_link_text:
                    try:
                        btn_num = el.text.split()[-1]
                        if btn_num.endswith("K"):
                            btn_num = float(btn_num[:-1]) * 1000
                        btn_num = int(btn_num)
                        reactions += btn_num
                    except ValueError:
                         continue

            views = parser.by_class(post, 'tgme_widget_message_views', True)

            if text:
                got_text += 1
            if link:
                link = link.get_attribute('href')
            if button_link:
                button_link = button_link.get_attribute('href')

            if text:
                parser.new_link(text, 'https://t.me/' + source[1:] + '/' +
                                str(post_id), 'telegram', (reactions, views))

            logger.info("%s %s %s %s %s %s %s", 'https://t.me/' + source[1:] + '/' +
                                str(post_id), views, reactions, link,
                         button_link, external_link_text, text)
            print("reactions", reactions)
            
        if num % 50 == 0:
            send("Parsed %s TG channels out of %s" % (num, len(channels)))
            
    parse_data = "Parsing process finished. Result:\n%s missed channels;\n" \
                 "%s new posts retrieved;\nTotal of %s channels parsed;\n" \
                 "Total time taken: %.2f minutes" % \
                 (len(missed), got_text, len(channels) - len(missed),
                  (time.time() - start) / 60)

    logger.info(parse_data)
    send(parse_data)


def get_channels(path):
    """
    Get Telegram channels from source file.
    :param path: str
    :return: set
    """
    channels = set()
    with open(path, 'r', encoding='UTF-8') as file:
        for line in file.readlines():
            if line.startswith('@'):
                channels.add(line)
    return channels


def get_date(date):
    """
    Getting date in the format %B %d.
    :param date: datetime.datetime
    :return: str
    """
    return date.strftime("%B %d").replace(" 0", " ")
