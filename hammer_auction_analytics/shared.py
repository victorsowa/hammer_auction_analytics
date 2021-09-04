import requests
from bs4 import BeautifulSoup


def get_page(url):
    return requests.get(url)


def get_soup(page_content):
    return BeautifulSoup(page_content, "html.parser")
