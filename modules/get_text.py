"""
This Module read data from json file
"""
import json


def read_text(filename):
    """
    This function get json_file and return information which I will use in future
    :param filename: json file
    :return: author, text, likes, shares, timestamp, links, comment_list
    """
    f = open(filename)
    json_file = json.load(f)
    author = json_file['author']
    text = json_file['post_text']
    likes = json_file['post_likes']
    shares = json_file['post_shares']
    timestamp = json_file['post_timestamp']
    links = json_file['post_links']
    comment_list = json_file['post_comments']
    return author, text, likes, shares, timestamp, links, comment_list
print(read_text('request_example.json'))

assert str(read_text('request_example.json')) == open('answer.txt').read()