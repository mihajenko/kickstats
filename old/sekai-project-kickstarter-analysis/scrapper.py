__author__ = 'Miha Jenko'

import os
import json
import pprint

from bs4 import BeautifulSoup


def load_page(path):
    with open(path, 'r', encoding='UTF-8') as fp:
        return fp.read()


def process_page(page):
    soup = BeautifulSoup(page, 'html5lib')
    rows = soup.select('.NS_backers__backing_row')
    backers = {}
    for row in rows:
        try:
            backers[row['data-cursor']] = row.div.h5.a.text
        except AttributeError:
            backers[row['data-cursor']] = ''
    return backers


def iterate_pages(base_dir=''):
    processed = []
    html_folder = os.path.join(os.getcwd(), 'html')
    for ppath in os.listdir(html_folder):
        page = load_page(os.path.join(html_folder, ppath))
        processed.append(process_page(page))
    return processed


def create_user_dictionary(projects):
    """
    Create a dictionary of all users spanning across all projects
    """
    _users = {}
    for project, i in zip(projects, range(len(projects))):
        for uid, name in project.items():
            if uid not in _users:
                _users[uid] = [i]
            else:
                _users[uid].append(i)
    return _users


if __name__ == '__main__':
    # get users from acrosss all projects
    users = create_user_dictionary(iterate_pages('html'))
    # print
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(users)
    # save
    with open('userdata.json', 'w', encoding='UTF-8') as f:
        json.dump(users, f)
