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

from datetime import datetime

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
        #yield ("mfnf" + str(rev["title"]), rev["user"].replace(" ", ""), event, rev["target"].split('/')[0], rev["timestamp"].rstrip("Z").replace("T", " "))
        yield ("mfnf" + str(rev["title"]), rev["user"].replace(" ", ""), event, "mfnf", rev["timestamp"].rstrip("Z").replace("T", " "))

created_articles = set()

with open(sys.argv[1], "r") as data:
    os.chdir(DIRECTORY)
    log_entries = (log_entry[:-1].split(sep='\t') for log_entry in data)
    #log_entries = ((article, username, event, "serlo/" + subject, date) for article, username, event, subject, date in log_entries)
    log_entries = sorted(itertools.chain(log_entries, mfnf_log()), key=lambda le: (le[4], le[2]))
    for article, username, event, subject, date in log_entries:
        assert event == "4" or event == "5"

        if subject != NULL:
            article_path = "{}/{}.txt".format(subject, article)

            timestamp = str(int(datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()))

            if is_ip(username):
                username = uniq_name(username)

            if event == "4" and article_path not in created_articles:
                modifier = "A"
                created_articles.add(article_path)
            else:
                modifier = "M"

            print("|".join([timestamp,username,modifier,article_path]))
