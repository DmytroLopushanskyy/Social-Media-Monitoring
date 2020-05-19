"""
Twitter parsing module
"""
import time
import requests
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, \
    StaleElementReferenceException, NoSuchElementException
from config import BOT_TOKEN, logger


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
            logger.info("likes_count: %s", likes)
            logger.info("retweets_count: %s", retweets)
            logger.info("reply_count: %s", replies)
        except (StaleElementReferenceException, NoSuchElementException):
            continue
        except Exception as e:
            logger.error("UNEXPECTED: " + str(e))
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
                logger.info("No Ukrainian text found!")
                continue

            if text:
                parser.new_link(text, url, "twitter", (likes, retweets, replies))
                all_tweets.add(tweet_unique_info)

        if "m" not in time_posted or "h" not in time_posted:
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
    available_time = 10 * 60 * 60 / len(keywords)  # 30 minutes total available
    logger.info("Maximum available time per word: %s seconds" % available_time)

    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.strftime("  %d").replace(" 0", "")
    logger.info("Starting parsing process. yesterday: %s", yesterday)
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
            except:
                logger.error("Error with proxy! Trying %s time" % i)
                i += 1
                proxies_iterations += 1
                if i % 20 == 0:
                    logger.info("Refreshing proxy list")
                    parser.browser = parser.browser_setup(iter=proxies_iterations,
                                                          update_proxies=True)
                elif i % 2 == 0:
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
                logger.info("IP Address Error. Changing it...")
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
                logger.info("IP Address exhausted. Changing it...")
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
