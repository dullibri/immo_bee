import os

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from immo_bee import scraping as scrap


class argImit:
    """Enables users to run the modules code interactively in notebook.

    Creates the class that would be created using the command line,
    e.g. 'python -m immo_bee schwerin haeuser kaufen'
    """

    locations = [["schwerin"]]
    path_json_folder = os.path.join(os.getcwd(), "..")
    rent = True
    buy = False
    appartment = True
    house = False
    path_csv_folder = "."


@pytest.fixture
def args():
    return argImit()


@pytest.fixture
def driver():
    """
    Initializes Firefox driver
    """

    options = Options()
    options.add_argument("--headless")
    _driver = webdriver.Firefox(options=options)
    yield _driver
    _driver.quit()


def test_make_urls(args):
    start_urls = scrap.make_immowelt_urls(args)
    assert start_urls == [
        "https://www.immowelt.de/liste/schwerin/wohnungen/mieten?sr=50&sort=distance"
    ]


def test_args(args, driver):
    url = "https://www.immowelt.de/liste/schwerin/wohnungen/mieten?sr=50&sort=distance"
    sel_soup = scrap.soup_get(url, driver)
    num_pages = scrap.n_pages(sel_soup)
    assert num_pages > 1
