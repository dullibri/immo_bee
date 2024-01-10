# This Python file uses the following encoding: utf-8
import concurrent.futures
import json
import logging
import os
import re
import time
from collections import OrderedDict
from datetime import date

import boto3
import certifi
import urllib3
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def prepare_urls(exposes):
    """Turns object ids into urls.

    Args:
        exposes (list): str representing object ids

    Returns:
        list: urls of objects
    """

    if re.findall(r".txt$", exposes):
        with open(exposes, "r") as f:
            exposes = f.read()
        if len(exposes) == 0:
            print("The file containing exposes could not be read.")

    exposes = exposes.split(sep=" ")
    url_root = "https://www.immowelt.de/expose/"
    return [url_root + a for a in exposes]


def get_tree(url):
    """Takes url and returns etree for parsing.

    Args:
        url (str)

    Returns:
        tree
    """
    http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())
    res = http.request("GET", url)
    parser = etree.HTMLParser(recover=True, encoding="utf-8")
    return etree.HTML(res.data, parser)


def get_right_list_elements(result):
    """Some of the results are empty - therefore, the try-except.
    Others are lists with more than one element and only specific
    elements are relevant.

    Args:
        result (dict of lists): result of the xpath elements.

    Returns:
        dict of strs
    """

    for key in [
        "title",
        "ort",
        "merkmale",
        "weitere_eigenschaften",
        "beschreibung",
        "anzahl_raeume",
        "wohnflaeche",
        "grundstuecksflaeche",
        "preis",
    ]:
        try:
            result[key] = result[key][0]
        except:
            pass

    return result


def checktype(obj):
    """Check if list is a list of strings, taken from
    https://stackoverflow.com/questions/
    18495098/python-check-if-an-object-is-a-list-of-strings

    Args:
        obj (ist): Potentially contains strings.

    Returns:
        boolean: True if object is a list of strings
    """
    return (
        bool(obj)
        and all(isinstance(elem, str) for elem in obj)
        and not all(len(elem) == 1 for elem in obj)
    )


def clean_whitespace(tmp_text):
    """Cleans whitespace from elements in list

    Args:
        tmp_text (list of str): [description]

    Returns:
        (list of str): [description]
    """

    if checktype(tmp_text):
        tmp_res = []
        for line in tmp_text:
            line_clean = re.sub(
                r"\r\n[ ]*", "", line
            )  # preceeding \r\n and whitespaces
            len_line = len(line_clean)
            if len_line == 0 or line_clean == " " * len_line:
                continue
            tmp_res.append(line_clean)
        return tmp_res
    else:  # only one str
        return re.sub(r"\r\n[ ]*|[ ]*$", "", tmp_text)


def scrape_data_from_xpath(url):
    """Reads the relevant elements from website and returns
    elements as dict.

    Args:
        url (str): url.

    Returns:
        dict: relevant elements from the respective website.
    """
    tree = get_tree(url)
    result = {}
    result["url"] = url
    xpath_patterns = xpath_patterns = {
        "title": "//title/text()",
        "ort": '//div[@class="location"]/span/text()',
        "adresse": "//span[@data-cy='address-city']//text()",
        "merkmale": "//li[@class='ng-star-inserted']//text()",
        "preis": '(//div[contains(@class,"hardfact")]//div[contains(string(),"preis") or contains(string(),"miete")]//text())[2]',  # response.xpath('//div[contains(@class,"hardfact")]//div//text()').getall()
        "anzahl_raeume": '//div[contains(@class,"hardfact") and contains(string(),"Zimmer")]/span//text()',
        "wohnflaeche": '//div[contains(@class,"hardfact") and contains(string(),"Wohnfl")]/span//text()',  #'//div[contains(@class,"hardfact")]//div[contains(string(),"Wohnfläche")]//text()',
        "grundstuecksflaeche": '//div[contains(@class,"hardfact") and contains(string(),"Grundst")]/span//text()',
        "weitere_eigenschaften": '//ul[@class="textlist_icon_03 padding_top_none "]//span//text()',
        "beschreibung": '//div[@class="section_content iw_right"]/p//text()',
        "energie": "//app-energy-equipment//text()",
    }
    for key, xpath_pattern in xpath_patterns.items():
        try:
            uncleanContent = tree.xpath(xpath_pattern)
        except:
            continue

        result[key] = uncleanContent

    return result


def scrape_object_pages(exposes):
    """Central scraping file for individual exposes.

    Args:
        exposes (list): expose ids (str)

    Returns:
        data: dict of scraped data.
    """

    data = {}
    data["objects"] = []

    urls = prepare_urls(exposes)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(scrape_data_from_xpath, urls)

    data["objects"] = [result for result in results]

    return data


def get_obj_and_transact_lists(arguments):
    """This function takes the boolean arguments returned by the getargs.py collecting
    command-line arguments and turns them into lists of strings needed for writing
    urls that are going to be scraped.

    Args:
        arguments (tuple): boolean arguments from the command-line arguments

    Returns:
        tuple of lists: list containing the German words for the transaction type
        (rent or buy) and for the object type (house or appartment)
    """

    rent, buy, house, appartment = (
        arguments.rent,
        arguments.buy,
        arguments.house,
        arguments.appartment,
    )
    objectTypeList = ["haeuser", "wohnungen"]
    if house:
        objectTypeList = ["haeuser"]
    elif appartment:
        objectTypeList = ["wohnungen"]
    transactionList = ["kaufen", "mieten"]

    if rent:
        transactionList = ["mieten"]
    elif buy:
        transactionList = ["kaufen"]

    return objectTypeList, transactionList


def make_immowelt_urls(arguments):
    """Creates a list of urls to be scraped for a list of locations for houses and/or
    apartments, buy and/or rent within a radius of 50 km.

    Args:
        arguments (tuple): contains the list of locations (locations) and optional parameters
        that can be specified in the command line, transaction-type (rent/buy) and object-type
        (house/appartment)

    Returns:
        list: urls as str, for loading individual objects.
    """

    radius = 50
    locations = arguments.locations[0]
    objectTypeList, transactionList = get_obj_and_transact_lists(arguments)

    urls = []
    for location in locations:
        for objectType in objectTypeList:
            for transaction in transactionList:
                tmpList = [
                    "https://www.immowelt.de/liste",
                    location,
                    objectType,
                    transaction,
                ]
                url = "/".join(tmpList)
                url = url + "?sr=" + str(radius) + "&sort=distance"
                urls.append(url)
    return urls


def make_output_file_name(url):
    """Create output file name.

    Args:
        url (str): url of object

    Returns:
        str: file name containting date, city, housing type, rent/buy with json suffix
    """
    rent_buy, city, flat_house = get_details_from_url(url)

    output_file_name = (
        str(date.today()) + "-" + city + "-" + flat_house + "-" + rent_buy + ".json"
    )
    return output_file_name


def dump_to_s3(bucket, data, url):
    """Sends data via put request to s3 bucket.

    Args:
        bucket (str): name of the bucket.
        data (dict): result of the scraping of one location and one type.
        url (str): url that has been scraped.

    """
    f_name = make_output_file_name(url)
    s3_client = boto3.client("s3")
    data_string = json.dumps(data, indent=2).encode("utf-8")
    try:
        r = s3_client.put_object(Bucket=bucket, Body=data_string, Key=f_name)
        r["f_name"] = f_name
        logging.info(r)
    except ClientError as e:
        logging.error(e)


def dump_to_json(data, url, arguments):
    """
    Dumps data to json.

    Creates a data path if necessary and dumps it as json. Regarding the file name
    see make_output_file_name.

    Args:
        data (dict): contains information on (multiple) housing object.
        url (str): url of the website being the starting point of the scraping.
        arguments (class): containing the settings for the scraping.
    """
    output_file_name = make_output_file_name(url)
    os.makedirs(arguments.data_folder, exist_ok=True)
    path_json = os.path.join(arguments.data_folder, output_file_name)
    print(f"files will be dumped here: {path_json}")

    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --- getting expose ids ---


def get_driver(headless=True):
    """
    Initializes Firefox driver
    """

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    return driver


def soup_get(url, driver):
    """
    retrieve BeautifulSoup Object form url and driver
    """
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    html = driver.execute_script("return document.documentElement.outerHTML")
    return BeautifulSoup(html, "html.parser")


def href_finder(soup_ele):
    """
    Finds all a["href"] in beautifulSoup object
    """
    return [a["href"] for a in soup_ele.findAll("a", href=True)]


def n_pages(sel_soup):
    """Get number of pages to search

    Args:
        hrefs (soup element): First page to start searching for object ids to scrape

    Returns:
        int: number of pages to search for hrefs.
    """
    buttons = sel_soup.select("button[class*=navNumberButton]")
    nPages = max(int(button.text) for button in buttons)
    return nPages


def expose_extr(hrefs):
    """Takes soup element of one search page of immowelt and returns
    all the exposes as list of str

    Args:
        hrefs (soup element): search page of immowelt

    Returns:
        list: exposes as strings
    """
    exposes = [re.findall("\/expose\/(\w+)", a) for a in hrefs]
    exposes = [a[0] for a in exposes if len(a) != 0]
    exposes = list(OrderedDict.fromkeys(exposes))
    return exposes


def get_details_from_url(url):
    """Read details (house/appartment, rent/buy, location) from url.

    Args:
        url (str): url of individual object

    Returns:
        tuple: rent_buy, location, flat_house
    """
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
    location = re.search(r"/liste/(.*?)/", url).group(1)
    return (rent_buy, location, flat_house)


def get_expose_ids(url_driver):
    """Searches a page for object ids. Needs to be a tuple for
    ThreadPool.executor. The latter only takes iterables,
    the driver is put in through a list of url_driver tuples.

    Args:
        url_driver (tuple): url and driver

    Returns:
        list: exposes as str.
    """
    url, driver = url_driver
    sel_soup = soup_get(url, driver)
    hrefs = href_finder(sel_soup)
    return expose_extr(hrefs)


def get_project_ids(headless=True, url=None, log_path="geckodriver.log"):
    """Takes a starting url and crawls through all other pages of a
    search and returns the expose ids.

    Args:
        headless (bool, optional): Refers to the webdriver. Defaults to True.
        url (str, optional): starting url of search. Defaults to None.

    Returns:
        str: expose ids separated by a blank.
    """
    Exposes = list()

    driver = get_driver(headless=headless)

    # get the first page and the total number of pages, num_pages
    sel_soup = soup_get(url, driver)
    hrefs = href_finder(sel_soup)
    num_pages = n_pages(sel_soup)
    Exposes = Exposes + expose_extr(hrefs)

    if num_pages > 1:
        urls = [url + "?cp=" + str(a) for a in range(2, num_pages + 1)]

        url_driver = (
            []
        )  # in order to pass the driver into the executor, an iterable is needed
        for url in urls:
            url_driver.append((url, driver))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(get_expose_ids, url_driver)

        Exposes_tmp = [expose for expose in results]
        Exposes_tmp = [item for sublist in Exposes_tmp for item in sublist]
        Exposes = Exposes + Exposes_tmp

    expose_ids = " ".join(Exposes)

    print(f"You have just retrieved {len(Exposes)} expose ids.")
    return expose_ids
