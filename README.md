# TrackMe - media-monitoring app for tracking your keywords across Twitter and Telegram
> First CS year coursework

TrackMe lets you track your keywords accross two social media platforms: Twitter and Telegram. It currently only supports Ukrainian keywords, tweets, and posts, and has only Ukrainian web interface. 

This project consists of two parts:
* 2 worker proccesses that perform parsing
* web application for displaying parsing results

The statistic we display for your keywords can be seen on the screenshot below.

![Screenshot from our website](https://user-images.githubusercontent.com/25267308/82360498-2b041c80-9a12-11ea-9691-cc72d80ae1b3.png)

## Installation

Install trackme using pip.

```
pip install trackme
```

## Usage example

If you only want to use our service, then go to [our website](https://newskitbot6.herokuapp.com/), register account, and follow the instructions there.

If you'd like to launch Telegram and Twitter parsing proccess, then you have to download our distributive and run it.

_For more examples and usage, please refer to the [Wiki][wiki]._

## Demo

You can watch our demo video [on YouTube](https://newskitbot6.herokuapp.com/)

## Development setup

Install requirements.txt using pip.

You also have to download chromedriver and set the correct enviromental variables in config.py

In this repository we do not include config.py, so you have to add it yourself. Here are the contents of it:

```
import logging
secret_key = 'YOUR_SECRET_KEY'
mongoclient = 'YOUR_MONGO_DB_KEY_LINK'
mongoname = 'YOUR_MONGO_DB_NAME'
NUMBER_WORDS = 20
flask_key = 'YOUR_FLASK_APP_SECRET_KEY'
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google-chrome'  # POSSIBLE CHROME PATH FOR LINUX
# CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'  # POSSIBLE CHROMEDRIVER PATH FOR LINUX

GOOGLE_CHROME_BIN = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' # POSSIBLE CHROME PATH FOR MAC
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'  # POSSIBLE CHROMEDRIVER PATH FOR MAC

logger = logging.getLogger("main_logger")  # SET UP LOGGER AND LOGGING LEVELS

```

## Meta

This project was developed by **Dmytro Lopushanskyy** and **Bohdan Vey**

Distributed under the MIT license. See ``LICENSE`` for more information.


## Contributing

1. Fork it (<https://github.com/DmytroLopushanskyy/Social-Media-Monitoring/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->
[wiki]: https://github.com/DmytroLopushanskyy/Social-Media-Monitoring/wiki
