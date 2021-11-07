import os

import requests
from bs4 import BeautifulSoup
import sqlalchemy

from db.db_session import global_init


DATABASE_NAME = "db.sqlite"


def initiate_db() -> sqlalchemy.engine.base.Engine:
    db_file = os.path.join(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", DATABASE_NAME)
    )
    return global_init(db_file)


def get_page(url):
    return requests.get(url)


def get_soup(page_content):
    return BeautifulSoup(page_content, "html.parser")
