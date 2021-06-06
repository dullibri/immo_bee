import re

import urllib3
from lxml import etree


def get_tree(url):
    http = urllib3.PoolManager()
    res = http.request("GET", url)
    parser = etree.HTMLParser(recover=True, encoding="utf-8")
    return etree.HTML(res.data, parser)


url = "https://www.immowelt.de/expose/2y3884z"
tree = get_tree(url)
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
result = {}
for key, value in xpath_patterns.items():
    # print(tree.xpath(value))
    result[key] = tree.xpath(value)


def get_right_list_elements(result):
    """Some of the results are empty - therefore the try-except. Others are lists with more than one element nd only
    specific elements are relevant.

    Parameters
    ----------
        - result : dict of lists
                   result of the xpath elements.

    Returns
    -------
        - result : dict of strings
    """
    for key in [
        "title",
        "ort",
        "merkmale",
    ]:  # ,'weitere_eigenschaften','beschreibung']:
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


result = get_right_list_elements(result)


def clean_whitespace(tmp_text):
    """Entfernt \r und \n und leere Zeilen sowohl aus
    Listen von Text als auch von Textteilen."""

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


remove_unwanted_elements(result)
