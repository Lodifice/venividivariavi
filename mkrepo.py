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

import logging
import os
import os.path
import sys

NULL = "NULL"
DEFAULT = "default"
DIRECTORY = "git"

if not os.path.isdir(DIRECTORY):
    os.system("git init '{}'".format(DIRECTORY))

article_locations = {}

with open(sys.argv[1], "r") as data:
    os.chdir(DIRECTORY)
    log_entries = sorted((log_entry[:-1].split(sep='\t') for log_entry in data), key=lambda le: (le[4], le[2]))
    for article, username, event, subject, date in log_entries:
        assert event == "4" or event == "5"
        if event == "4":
            # create article
            if subject == NULL:
                logging.warning("Attempted creation of article without subject ({}, {}, {}, {}, {})".format(article, username, event, subject, date))
                subject = DEFAULT
            os.makedirs(subject, exist_ok=True)
            article_path = "/".join((subject, article))
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
            article_path = "/".join((article_locations[article], article))
            with open(article_path, "a") as article_file:
                print(date, username, file=article_file)
            os.system("git add '{}'".format(article_path))
            os.system("GIT_COMMITTER_DATE='{}' git commit --allow-empty-message -m 'edit {}' --author '{} <{}@serlo.org>' --date '{}'".format(date, article_path, username, username, date))
