import re
import time
from itertools import chain
from collections import OrderedDict
from bs4 import BeautifulSoup
from selenium import webdriver
import geckodriver_autoinstaller
from selenium.webdriver.firefox.options import Options
from google.cloud import storage
# from google.oauth2 import service_account
import os


def soup_get(url, driver):
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    html = driver.execute_script('return document.documentElement.outerHTML')
    return BeautifulSoup(html, 'html.parser')


def href_finder(soup_ele):
    return [a['href'] for a in soup_ele.findAll('a', href=True)]


def n_pages(hrefs):
    cps = [re.findall('cp=(\w+)', a) for a in hrefs]
    cps = list(filter(None, cps))
    return max([int(b[0]) for b in cps])


def href_extr(hrefs):
    """
    Takes soup element of one search page of immowelt and returns
    all the hrefs as list of str
    """
    exposes = [re.findall('\/expose\/(\w+)', a) for a in hrefs]
    exposes = [a[0] for a in exposes if len(a) != 0]
    exposes = list(OrderedDict.fromkeys(exposes))
    return exposes


def get_driver(headless=True):
    options = Options()
    options.headless = headless
    driver = webdriver.Firefox(options=options)
    return driver


def projekt_finder(hrefs):
    projekts = [re.findall('\/projekte\/expose\/(\w+)', a) for a in hrefs]
    projekts = list(filter(None, projekts))
    projekts = [*projekts]
    return list(set(chain.from_iterable(projekts)))


def get_data(url, headless=True, test_num=None):
    Exposes = list()
    Projekte = list()

    driver = get_driver(headless)

    # get the first page and the total number of pages, num_pages
    sel_soup = soup_get(url, driver)
    hrefs = href_finder(sel_soup)
    num_pages = n_pages(hrefs)
    Exposes = Exposes + href_extr(hrefs)
    Projekte = Projekte + projekt_finder(hrefs)

    if test_num is not None:
        num_pages = test_num

    for a in range(2, num_pages):  # +1):
        new_url = url+'?cp='+str(a)
        soup_new = soup_get(new_url, driver)
        href_new = href_finder(soup_new)
        Exposes = Exposes+href_extr(href_new)
        Projekte = Projekte + projekt_finder(href_new)
    Projekte_text = " ".join(Projekte)
    Exposes_text = " ".join(Exposes)

    return Exposes_text, Projekte_text


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # storage_client = storage.Client(credentials=credentials)
    storage_client = storage.Client()

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


# bucket_name = "immobilienpreise"
# source_file_name = Exposes_text
# destination_blob_name = "Projekte_n.txt"
# upload_blob(bucket_name, source_file_name, destination_blob_name)


def greeting(request):
    return "hochgeladen"


# with open('ExposeBerlin.txt','w') as f:
    # f.write(str(Exposes))
credential_path = "servaccount.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
url = 'https://www.immowelt.de/liste/berlin/wohnungen/kaufen'
