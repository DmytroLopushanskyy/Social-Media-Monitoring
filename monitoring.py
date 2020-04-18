from classes.keyword import words
from classes.user import User, get_all_users

links = []


def new_link(text, link):
    """
    This function get information about post, and
    update weights of keywords and user to get most popular one
    :param text: str
    :param link: str
    :return: None
    """
    words.add_new_link(text, link)
    global users
    for user in users:
        user.check_user_weight(link)


def update():
    """
    This function push information into database
    :return: None
    """
    global users
    for user in users:
        user.update_links()


users = get_all_users()

new_link('1 2 3 1 2 3 1 2', '17')
new_link('1 2', '18')
new_link('1234', '19')
new_link('1234 1234 1234 1234 1234 1234', '20')
new_link('1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1', '21')
new_link('1 1 1', '22')
new_link('1 1 1 1 1', '23')
update()
