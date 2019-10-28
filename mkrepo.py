# mkrepo.py - Create a git repository from structured edit data
#
# Written in 2019 by Richard Mörbitz
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without
# any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

import itertools
import logging
import os
import os.path
import sys

import create_mfnf_git

NULL = "NULL"
DEFAULT = "default"
DIRECTORY = "git"

USER = {}
NO = 1

def uniq_name(address):
    global USER
    global NO

    if address not in USER:
        USER[address] = " " * NO
        NO+=1

    return USER[address]

def is_ip(address):
    import ipaddress

    try:
        ipaddress.ip_address(address)

        return True
    except ValueError:
        return False

if not os.path.isdir(DIRECTORY):
    os.system("git init '{}'".format(DIRECTORY))

article_locations = {}

def mfnf_log():
    mfnf_sitemap = create_mfnf_git.parse_sitemap()
    created_articles = set()
    for rev in mfnf_sitemap.revisions():
        if rev["title"] in created_articles:
            event = "5"
        else:
            event = "4"
            created_articles.add(rev["title"])
        yield ("mfnf" + str(rev["title"]), rev["user"].replace(" ", ""), event, "mfnf/" + rev["target"].split('/')[0], rev["timestamp"].rstrip("Z").replace("T", " "))

with open(sys.argv[1], "r") as data:
    os.chdir(DIRECTORY)
    log_entries = (log_entry[:-1].split(sep='\t') for log_entry in data)
    #log_entries = ((article, username, event, "serlo/" + subject, date) for article, username, event, subject, date in log_entries)
    log_entries = sorted(itertools.chain(log_entries, mfnf_log()), key=lambda le: (le[4], le[2]))
    for article, username, event, subject, date in log_entries:
        if is_ip(username):
            username = uniq_name(username)

        assert event == "4" or event == "5"
        if event == "4":
            # create article
            if subject == "serlo/" + NULL:
                logging.warning("Skip creation of article without subject ({}, {}, {}, {}, {})".format(article, username, event, subject, date))
                continue
                subject = DEFAULT
            os.makedirs(subject, exist_ok=True)
            article_path = "/".join((subject, article)) + ".txt"
            if os.path.isfile(article_path):
                logging.warning("Skipping newly created article that already exists ({}, {}, {}, {}, {})".format(article, username, event, subject, date))
                continue
            with open(article_path, "w") as article_file:
                print(date, username, file=article_file)
            article_locations[article] = subject
            os.system("git add '{}'".format(article_path))
            os.system("GIT_COMMITTER_DATE='{}' git commit --allow-empty-message -m 'create {}' --author '{} <{}@serlo.org>' --date '{}'".format(date, article_path, username, username, date))
        else:
            # update article
            if subject != NULL:
                logging.warning("Edit of article has subject ({}, {}, {}, {}, {})".format(article, username, event, subject, date))
            if article not in article_locations:
                logging.warning("Skipping edit of non-existing article ({}, {}, {}, {}, {})".format(article, username, event, subject, date))
                continue
            article_path = "/".join((article_locations[article], article)) + ".txt"
            with open(article_path, "a") as article_file:
                print(date, username, file=article_file)
            os.system("git add '{}'".format(article_path))
            os.system("GIT_COMMITTER_DATE='{}' git commit --allow-empty-message -m 'edit {}' --author '{} <{}@serlo.org>' --date '{}'".format(date, article_path, username, username, date))
