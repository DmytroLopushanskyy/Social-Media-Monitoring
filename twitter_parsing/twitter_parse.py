"""
Twitter parsing module
"""
import time
import requests
import logging
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, \
    StaleElementReferenceException, NoSuchElementException
from config import BOT_TOKEN


def send(text):
    requests.get(
        'https://api.telegram.org/bot%s/sendMessage?chat_id=138918380&text=%s'
        % (BOT_TOKEN, text))
    requests.get(
        'https://api.telegram.org/bot%s/sendMessage?chat_id=426055346&text=%s'
        % (BOT_TOKEN, text))


def get_tweet_interactions(tweet, interaction):
    """
    Returns interaction count based on its name and tweet data
    :param tweet: Selenium WebElement
    :param interaction: str (like, retweet, reply)
    :return: str
    """
    count = tweet.find_element_by_css_selector(
        'div[data-testid="' + interaction + '"]')
    count = count.get_attribute('aria-label')
    count = [int(s) for s in count.split() if s.isdigit()]
    if not count:
        count = [0]
    return count[0]


def parse_tweets(browser, all_tweets, yesterday, parser):
    """
    Parse all tweets from search page.
    :param browser: Selenium browser
    :param all_tweets: set
    :return: bool or str. True if parsing is over. False otherwise.
    'error' if an error message appears
    """
    print("parse_tweets")
    tweets = browser.find_elements_by_css_selector(
             'div[data-testid="tweet"]')
    for tweet in tweets:
        try:
            acc = tweet.find_element_by_css_selector('div[dir="ltr"]').\
                find_element_by_tag_name('span').text
            time_posted = tweet.find_element_by_tag_name('time').text
            links = tweet.find_elements_by_css_selector('a[role="link"]')
            for link in links:
                url = link.get_attribute('href')
                if len(url.split('/')) == 6:
                    print(url)
                    break
            likes = get_tweet_interactions(tweet, "like")
            retweets = get_tweet_interactions(tweet, "retweet")
            replies = get_tweet_interactions(tweet, "reply")
            logging.info("likes_count: %s", likes)
            logging.info("retweets_count: %s", retweets)
            logging.info("reply_count: %s", replies)
        except (StaleElementReferenceException, NoSuchElementException):
            continue
        except Exception as e:
            logging.error("UNEXPECTED: " + str(e))
            return 'error'
        tweet_unique_info = acc, time_posted

        if tweet_unique_info not in all_tweets:
            text = ""
            try:
                spans = tweet.find_element_by_css_selector('div[lang="uk"]'). \
                    find_elements_by_tag_name('span')
                for child in spans:
                    text += child.text
                print(text)
            except (StaleElementReferenceException, NoSuchElementException):
                logging.info("No Ukrainian text found!")
                continue

            if text:
                parser.new_link(text, url, "twitter", (likes, retweets, replies))
                all_tweets.add(tweet_unique_info)

        if time_posted.endswith(yesterday):
            return True
    return False


def parse_twitter(parser):
    """
    Main Twitter posts parsing function.
    :param parser: Parser
    :param keywords: list
    :return: None
    """
    start = time.time()
    print(start)
    keywords = parser.keywords.keywords
    browser = parser.browser
    available_time = 0.5 * 60 * 60 / len(keywords)  # 10 hours total available
    logging.info("Maximum available time per word: %s seconds" % available_time)

    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.strftime("  %d").replace(" 0", "")
    logging.info("Starting parsing process. yesterday: %s", yesterday)
    send("Starting parsing process.")
    proxies_iterations = 0

    for ind, keyword in enumerate(keywords):
        print(keyword)
        i = 0
        loaded = False
        while not loaded:
            try:
                url = 'https://twitter.com/search?q=' + keyword + '%20lang%3Auk&f=live'
                browser.get(url)
                WebDriverWait(browser, 7).until(
                    expected_conditions.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'section[aria-labelledby="accessible-list-0"]')))
                loaded = True
            except TimeoutException:
                i += 1
                proxies_iterations += 1
                if i % 10 == 0:
                    logging.error("Proxy error! Trying %s time with renewal" % i)
                    parser.browser = parser.browser_setup(iter=proxies_iterations,
                                                          update_proxies=True)
                elif i % 2 == 0:
                    logging.error("Error with proxy! Trying %s time" % i)
                    parser.browser = parser.browser_setup(proxies_iterations)


        if not loaded:
            continue

        main_start = time.time()
        print(main_start)

        all_tweets = set()
        finished = False
        last_len = 0
        stop_parsing_count = 0
        iterations = 0
        while not finished and time.time() - main_start < available_time * (ind + 1):
            finished = parse_tweets(browser, all_tweets, yesterday, parser)
            if finished == 'error':
                logging.info("IP Address Error. Changing it...")
                send("IP Address Error. Changing it...")
                proxies_iterations += 1
                parser.browser = parser.browser_setup(proxies_iterations)
                finished = True
                continue
            browser.execute_script("window.scrollTo(0,  document.body.scrollHeight)")
            print(iterations, stop_parsing_count, len(all_tweets), (time.time() - start) / 60, all_tweets)
            if len(all_tweets) == last_len:
                stop_parsing_count += 1
            else:
                stop_parsing_count = 0
            if stop_parsing_count == 100:
                logging.info("IP Address exhausted. Changing it...")
                send("IP Address exhausted. Changing it...")
                send("Parsed %s tweets for word %s" % (last_len, keyword))
                proxies_iterations += 1
                parser.browser = parser.browser_setup(proxies_iterations)
                finished = True
                continue
            iterations += 1
            last_len = len(all_tweets)

        send("Parsed %s tweets for word %s. Taken %s minutes" %
             (len(all_tweets), keyword, (time.time() - main_start)/60))



    #     tweets = browser.find_elements_by_css_selector(
    #         'div[data-testid="tweet"]')
    #     for post in tweets:
    #         post_date = post.find_element_by_class_name('tgme_widget_message'
    #                                                     '_service_date_wrap')\
    #             .find_element_by_class_name('tgme_widget_message_service_date')
    #         post_date = post_date.get_attribute('innerHTML')
    #         if post_date not in yesterday:
    #             break
    #
    #         post = post.find_element_by_class_name('tgme_widget_message')
    #         post_id = post.get_attribute('data-post').split('/')[1]
    #
    #         link = parser.by_class(post, 'tgme_widget_message_link_preview')
    #         text = parser.by_class(post, 'tgme_widget_message_text', True)
    #         button_link = parser.\
    #             by_class(post, 'tgme_widget_message_inline_button')
    #         external_link_text = parser.\
    #             by_class(post, 'tgme_widget_message_inline_button_text', True)
    #         views = parser.by_class(post, 'tgme_widget_message_views', True)
    #         reactions = 0
    #
    #         if text:
    #             got_text += 1
    #         if link:
    #             link = link.get_attribute('href')
    #         if button_link:
    #             button_link = button_link.get_attribute('href')
    #         if button_link == 'https://t.me/' + source[1:] + '/' + \
    #                 str(post_id):
    #             reactions_list = post.find_elements_by_class_name(
    #                 'tgme_widget_message_inline_button_text')
    #             for reaction_div in reactions_list:
    #                 react_num = re.search(r'\d+', reaction_div.text)
    #                 if react_num:
    #                     reactions += int(react_num.group())
    #
    #         logging.info("%s %s %s %s %s %s", views, reactions, link,
    #                      button_link, external_link_text, text)
    #
    # logging.info("Parsing process finished. Result:\n%s missed channels;\n"
    #              "%s new posts retrieved;\nTotal of %s channels parsed;\n"
    #              "Total time taken: %.2f minutes",
    #              len(missed), got_text, len(channels) - len(missed),
    #              (time.time() - start) / 60)

