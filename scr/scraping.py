import concurrent.futures
import json
import re

import urllib3
from lxml import etree


def prepare_urls(exposes):
    """takes list or txt.file (path) containing expose-ids, returns list of urls"""

    if re.findall(r".txt$", exposes):
        with open(exposes, "r") as f:
            exposes = f.read()
        if len(exposes) == 0:
            print("The file could not be read.")

    exposes = exposes.split(sep=" ")
    url_root = "https://www.immowelt.de/expose/"
    return [url_root + a for a in exposes]


def get_id_from_url(url):
    """Returns object id from url"""
    id = re.search(r"(?<=expose\/).*", url)
    return id.group(0)


def get_tree(url):
    http = urllib3.PoolManager()
    res = http.request("GET", url)
    parser = etree.HTMLParser(recover=True, encoding="utf-8")
    return etree.HTML(res.data, parser)


def get_right_list_elements(result):
    """Some of the results are empty - therefore, the try-except. Others are lists with more than one element nd only
    specific elements are relevant.

    Args
    ----------
        - result : dict of lists
                   result of the xpath elements.

    Returns
    -------
        - result : dict of strings
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
    """Check if list is a list of strings, taken from  https://stackoverflow.com/questions/18495098/python-check-if-an-object-is-a-list-of-strings"""
    return (
        bool(obj)
        and all(isinstance(elem, str) for elem in obj)
        and not all(len(elem) == 1 for elem in obj)
    )


def clean_whitespace(tmp_text):
    """Cleans whitespace from elements in list"""

    if checktype(tmp_text):  # liste von str

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
    else:  # nur ein str
        return re.sub(r"\r\n[ ]*|[ ]*$", "", tmp_text)


def remove_unwanted_elements(result):
    for key, value in result.items():
        try:
            result[key] = clean_whitespace(result[key])
        except:
            continue
    return result


def read_data_from_xpath(url):
    """Liest die Webseite und legt die gesuchten Element in data (dict) ab."""
    tree = get_tree(url)
    result = {}
    result["url"] = url
    xpath_patterns = {
        "title": "//title/text()",
        "ort": '//div[@class="location"]/span/text()',
        "merkmale": '//div[@class="merkmale"]/text()',
        #'stadteilbewertung':'//div[contains(@id,"divRating")]',
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


def scrape_individual_object(url):
    id = get_id_from_url(url)  # is this still needed?
    obj_data = read_data_from_xpath(url)
    return obj_data


def scrape_object_pages(exposes):
    """Main scrape file, takes exposes (list of ids as str), returns data"""
    data = {}
    data["objects"] = []

    urls = prepare_urls(exposes)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(scrape_individual_object, urls)

    data["objects"] = [result for result in results]

    return data


def make_immowelt_urls(arguments):
    """
    creates a list of urls to be scraped for a list of locations for houses and
    apartments, buy and rent within a radius of 50 km.

         paramters:
             locationList (list): strings containing the location names AS
                                 IMMOWELT writes them.

         results:
             urls (list)
    """
    radius = 50
    locations, rent, buy, house, appartment, _ = arguments
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
