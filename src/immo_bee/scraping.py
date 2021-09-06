import concurrent.futures
import json
import os
import re
import time
from collections import OrderedDict
from datetime import date

import urllib3
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
    http = urllib3.PoolManager()
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

    for key in ["title", "ort", "merkmale", "weitere_eigenschaften", "beschreibung"]:
        try:
            result[key] = result[key][0]
        except:
            pass
    for key in ["preis", "anzahl_raeume", "wohnflaeche", "grundstuecksflaeche"]:
        try:
            result[key] = result[key][1]
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


def remove_unwanted_elements(result):
    """cleans result dict of xpath-scraping of individual objects of unwanted
    whitespaces.

    Args:
        result (dict): contains list of strings that are the result of xpath scraping

    Returns:
        dict: each list in original dict cleaned of whitespaces.
    """
    for key in result.keys():
        try:
            result[key] = clean_whitespace(result[key])
        except:
            continue
    return result


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
    xpath_patterns = {
        "title": "//title/text()",
        "ort": '//div[@class="location"]/span/text()',
        "merkmale": '//div[@class="merkmale"]/text()',
        "preis": '//div[contains(@class,"hardfact")]//div[contains(string(),"preis") or contains(string(),"miete")]//text()',  # response.xpath('//div[contains(@class,"hardfact")]//div//text()').getall()
        "anzahl_raeume": '//div[contains(@class,"hardfact")]//div[contains(string(),"Zimmer")]//text()[1]',
        "wohnflaeche": '//div[contains(@class,"hardfact")]//div[contains(string(),"Wohnfläche")]//text()',
        "grundstuecksflaeche": '//div[contains(@class,"hardfact")]//div[contains(string(),"Grundstücksfl.")]//text()',
        "weitere_eigenschaften": '//ul[@class="textlist_icon_03 padding_top_none "]//span//text()',
        "beschreibung": '//div[@class="section_content iw_right"]/p//text()',
    }
    for key, xpath_pattern in xpath_patterns.items():
        try:
            uncleanContent = tree.xpath(xpath_pattern)
        except:
            continue

        result[key] = uncleanContent
    result = get_right_list_elements(result)
    result = remove_unwanted_elements(result)
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


def dump_to_json(data, url):
    """Takes data and dumps it to json in (newly to be created)
    data folder.

    Args:
        data (dict): scraping output
        oldName (str): name with suffix ".txt"
    """
    rent_buy, city, flat_house = get_details_from_url(url)

    output_file_name = (
        str(date.today()) + "-" + city + "-" + flat_house + "-" + rent_buy + ".json"
    )

    path = os.getcwd()
    path_data = os.path.join(path, "data", output_file_name)
    pathDataFolder = os.path.join(path, "data")
    if not os.path.exists(pathDataFolder):
        os.makedirs(pathDataFolder)

    with open(path_data, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --- getting expose ids ---


def get_driver(headless=True, log_path="geckodriver.log"):
    """
    Initializes Firefox driver
    """
    options = Options()
    options.headless = headless
    driver = webdriver.Firefox(options=options, service_log_path=log_path)
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


def n_pages(hrefs):
    """Get number of pages to search

    Args:
        hrefs (soup element): First page to start searching for object ids to scrape

    Returns:
        int: number of pages to search for hrefs.
    """
    cps = [re.findall("cp=(\w+)", a) for a in hrefs]
    cps = list(filter(None, cps))
    nPages = max([int(b[0]) for b in cps], default=1)
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


def get_project_ids(headless=True, url=None):
    """Takes a starting url and crawls through all other pages of a
    search and returns the expose ids.

    Args:
        headless (bool, optional): Refers to the webdriver. Defaults to True.
        url (str, optional): starting url of search. Defaults to None.

    Returns:
        list: expose ids as strings
    """
    Exposes = list()

    driver = get_driver(headless=headless)

    # get the first page and the total number of pages, num_pages
    sel_soup = soup_get(url, driver)
    hrefs = href_finder(sel_soup)
    num_pages = n_pages(hrefs)
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

    Exposes_text = " ".join(Exposes)

    print(f"You have just retrieved {len(Exposes)} expose ids.")
    return Exposes_text