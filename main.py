import os
from google.cloud import storage
from datetime import date
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from collections import OrderedDict
from itertools import chain
import time
import re
from scr.scraping import *
from scr.cleaning import *
import json

def get_driver(headless=True):
    """
    Initializes Firefox driver
    """
    options = Options()
    options.headless = headless
    driver = webdriver.Firefox(options=options)
    return driver


def soup_get(url, driver):
    """
    retrieve BeautifulSoup Object form url and driver
    """
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    html = driver.execute_script('return document.documentElement.outerHTML')
    return BeautifulSoup(html, 'html.parser')


def href_finder(soup_ele):
    """
    Finds all a["href"] in beautifulSoup object
    """
    return [a['href'] for a in soup_ele.findAll('a', href=True)]


def n_pages(hrefs):
    """
    Get number of pages to search
    """
    cps = [re.findall('cp=(\w+)', a) for a in hrefs]
    cps = list(filter(None, cps))
    nPages = max([int(b[0]) for b in cps],default=1)
    return nPages



def href_extr(hrefs):
    """
    Takes soup element of one search page of immowelt and returns
    all the hrefs as list of str
    """
    exposes = [re.findall('\/expose\/(\w+)', a) for a in hrefs]
    exposes = [a[0] for a in exposes if len(a) != 0]
    exposes = list(OrderedDict.fromkeys(exposes))
    return exposes


def projekt_finder(hrefs):
    """
    Some of the Exposes are featured projects identified here
    """
    projekts = [re.findall('\/projekte\/expose\/(\w+)', a) for a in hrefs]
    projekts = list(filter(None, projekts))
    projekts = [*projekts]
    return list(set(chain.from_iterable(projekts)))


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


def write_to_disc(destination_blob_name, Exposes):
    with open(destination_blob_name,  "w") as f:
        f.write(Exposes)


test = 'https://www.immowelt.de/liste/ratzeburg/haeuser/kaufen?lat=53.6943&lon=10.7919&sr=50&sort=distance'


def get_details_from_url(url):
    """
    input: url, str
    output: (rent_buy, city, flat_house), tuple
    """
    flat_house = "wohnungen"
    if re.search("haeuser", url):
        flat_house = "haus"
    rent_buy = "mieten"
    if re.search("kaufen", url):
        rent_buy = "kaufen"
    city = re.search(r'/liste/(.*?)/', url).group(1)
    return (rent_buy, city, flat_house)



def get_project_ids(bucket_name, headless=True, url=None, city="berlin", flat_house="wohnungen", rent_buy="kaufen", to_disc=False):
    if url:
        rent_buy, city, flat_house = get_details_from_url(url)
    else:
        url = 'https://www.immowelt.de/liste/'+city+'/'+flat_house+'/'+rent_buy

    destination_blob_name = str(date.today())+"-"+city+"-"+flat_house+"-"\
        + rent_buy+".txt"
    Exposes = list()

    driver = get_driver(headless=headless)

    # get the first page and the total number of pages, num_pages
    sel_soup = soup_get(url, driver)
    hrefs = href_finder(sel_soup)
    num_pages = n_pages(hrefs)

    Exposes = Exposes + href_extr(hrefs)

    if num_pages >1:

        for a in range(2, num_pages):  # +1):
            new_url = url+'?cp='+str(a)
            soup_new = soup_get(new_url, driver)
            href_new = href_finder(soup_new)
            Exposes = Exposes+href_extr(href_new)

    Exposes_text = " ".join(Exposes)
    if to_disc:
        write_to_disc(destination_blob_name, Exposes_text)
    else:
        upload_blob(bucket_name, Exposes_text, destination_blob_name)
    print(f'You have just retrieved {len(Exposes)} exposes.')
    return Exposes_text, destination_blob_name

def txt_to_json(oldName):
    return re.sub(r'.txt','.json',oldName)

def dump_to_json(data, oldName):
    newName = txt_to_json(oldName)
    path = os.getcwd()
    path_data = os.path.join(path, "data", newName)
    pathDataFolder = os.path.join(path,"data")
    if not os.path.exists(pathDataFolder):
        os.makedirs(pathDataFolder)

    with open(path_data, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def process_url(url):
    Exposes_text, destination_blob_name = get_project_ids(bucket_name, url = url, to_disc=True)
    data = scrape_object_pages(Exposes_text)
    dump_to_json(data,destination_blob_name)
    print(destination_blob_name,' processed.')
    


if __name__ == "__main__":
    credential_path = "credentials.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    bucket_name = 'immobilienpreise'
    locations = ["berlin","ratzeburg","ludwigslust-meckl","luebeck-hansestadt","wismar"]
    #locations = ["norderstedt"]

    urls = make_immowelt_urls(locationList = locations)
    for url in urls:
        process_url(url)
    df = load_and_prepare_data()
    save_data_as_excel(df)

