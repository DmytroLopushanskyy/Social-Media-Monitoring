"""
Filter telegram channels based on their subscribers number. (only > 500)
"""
from bs4 import BeautifulSoup
import requests
from telegram_parsing.tg_parse import get_channels


def channel_has_more_subscribers_than(channel, num):
    """
    Returns True if channel has more than num subsribers.
    :param channel: str
    :param num: int
    :return: bool
    """
    if channel.startswith("@"):
        channel = "https://t.me/" + channel[1:]
        print(channel)

    data = requests.get(channel, verify=False).text
    print(data)
    soup = BeautifulSoup(data, "lxml")
    try:
        subscribers = soup.find("div", {"class": "tgme_page_extra"}).get_text()
        print(subscribers)
        subscribers = subscribers.replace(" ", "")
        subscribers = subscribers.replace("members", "")
        subscribers = int(subscribers)
        print(subscribers)

        if subscribers > num:
            return True
        return False
    except Exception as error:
        print("Error!", error)
        return False


def main():
    """
    Starts channels analysis.
    :return: None
    """
    channels = get_channels('telegram_parsing/channels.txt')
    filtered_channels = set()
    i = 0
    for chan in channels:
        i += 1
        print("statistics", i, len(channels), len(filtered_channels))
        if channel_has_more_subscribers_than(chan, 500):
            filtered_channels.add(chan)

    print(filtered_channels)


if __name__ == '__main__':
    main()
