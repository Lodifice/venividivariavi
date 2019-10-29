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

article_locations = {}

def mfnf_log():
    for page in create_mfnf_git.mfnf_pages():
        first = False

        for i, rev in zip(itertools.count(), create_mfnf_git.revisions(page)):
            event = "4" if i == 0 else "5"

            #yield ("mfnf" + str(rev["title"]), rev["user"].replace(" ", ""), event, rev["target"].split('/')[0], rev["timestamp"].rstrip("Z").replace("T", " "))
            yield ("mfnf" + page.replace("/", "-"), rev["user"], event, "mfnf", rev["timestamp"].rstrip("Z").replace("T", " "))

created_articles = set()

with open(sys.argv[1], "r") as data:
    log_entries = (log_entry[:-1].split(sep='\t') for log_entry in data)
    log_entries = itertools.chain(log_entries, mfnf_log())
    #log_entries = ((article, username, event, "serlo/" + subject, date) for article, username, event, subject, date in log_entries)
    log_entries = ((article, username, event, subject, int(datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp())) for article, username, event, subject, date in log_entries)
    log_entries = sorted(log_entries, key=lambda le: (le[4], le[2]))
    for article, username, event, subject, date in log_entries:
        assert event == "4" or event == "5"

        if subject != NULL:
            article_path = "{}/{}.txt".format(subject, article)

            if is_ip(username):
                username = uniq_name(username)

            if event == "4" and article_path not in created_articles:
                modifier = "A"
                created_articles.add(article_path)
            else:
                modifier = "M"

            params = [str(date),username,modifier,article_path]
            params = [x.replace("|", "-") for x in params]

            print("|".join(params))
