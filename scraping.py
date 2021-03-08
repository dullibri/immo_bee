import urllib3
from lxml import etree
import re
# Erledigt: lxml.tree und response verwendet, um die Seiten zu scapen.
# Die wichtigsten Eigenschaften können gelesen werden
# To do:
# 1. Die Eigenschaften müssen Art-übergreifend (miete, kaufen, haus, wohnung)
#  unabhängig mit try-except Konstrukten gelesen werden.
# 2. Das scraping muss in main integriert werden.
# 3. Das scraping muss bereinigt werden ("\nr     ", bspw. muss raus, nach einem ":"
# muss eine Ausprägung als solche erkannt werden.)
test = '2021-02-28-hamburg-haeuser-kaufen.txt'
test = '2021-02-28-hamburg-wohnungen-kaufen.txt'
test = '2021-02-28-ludwigslust-meckl-haus-mieten.txt'

def prepare_urls(filename):
    """read text_file containing expose-ids, return list of urls"""
    with open(filename, "r") as f:
        exposes = f.read()
    exposes = exposes.split(sep=" ")
    url_root = 'https://www.immowelt.de/expose/'
    return [url_root+a for a in exposes]

urls =prepare_urls(test)

def get_id_from_url(url):
    id = re.search(r'(?<=expose\/).*',url)
    return id.group(0)


def scrape_houses(urls):
    data = {}
    request = urllib3.PoolManager()

    for url in urls:

        res = request.request("GET", url)
        parser = etree.HTMLParser(recover=True)
        tree = etree.HTML(res.data, parser)
        id = get_id_from_url(url)

        try:
            data[id] ={
                'url':url,
                'title': tree.xpath('//title/text()')[0],
                'ort': tree.xpath('//div[@class="location"]/span/text()'),
                'merkmale':  tree.xpath('//div[@class="merkmale"]/text()'),
                'stadteilbewertung':  tree.xpath('//div[contains(@id,"divRating")]'),
                'kaufpreis': tree.xpath('//div[@class="hardfact"]/strong/strong/text()'),
                'anzahl_raeume': tree.xpath('//div[@class="hardfact rooms"]/text()'),
                'wohnflaeche': tree.xpath('//div[@class="hardfact "]/text()')[3],
                'grundstuecksflaeche': tree.xpath('//div[@class="hardfact "]/text()')[5],
                #'energielabel': tree.xpath('//div[@class="datatable energytable clear"]/div/span[@class="datalabel"]/text()')[0],
                #'energiemerkmale': tree.xpath('//div[@class="datatable energytable clear"]/div/span[@class="datacontent"]/text()')[0],
                #'energiemerkmale_checkbox':tree.xpath('//ul[contains(string(),"Haustyp")]//text()'),
                #'objektbeschreibung':tree.xpath('//div[contains(string(),"Objektbeschreibung")]//p/text()'),
                }
        except:
            print("id ",id," could not be retrieved. Most likely, it has been taken offline.")
    return data

data = scrape_houses(urls)
data

url = urls[0]
url='https://www.immowelt.de/expose/2xcl64z'

res = request.request("GET", url)
parser = etree.HTMLParser(recover=True)
tree = etree.HTML(res.data, parser)
id = get_id_from_url(url)
data = {}
data[id] = {}
data[id]['url'] = url
data
try:
    data[id]['title'] = tree.xpath('//title/text()')[0]
except:
    print('id: ',id, ' not tile could be retrieved')
try:
    data[id]['ort'] = tree.xpath('//div[@class="location"]/span/text()')
except:
    print('id: ',id, ' no location(ort) could be retrieved')
try:
    data[id]['merkmale'] = tree.xpath('//div[@class="merkmale"]/text()')
except:
    print('id: ',id, ' no characteristics(merkmale) could be retrieved')
try:
    data[id]['stadteilbewertung'] =  tree.xpath('//div[contains(@id,"divRating")]')
except:
    print('id: ',id, ' no rating(stadteilbewertung) could be retrieved')
try:
    data[id]['preis'] =  tree.xpath('//div[@class="hardfact"]/strong/strong/text()')
except:
    print('id: ',id, ' no price(preis) could be retrieved')
try:
    data[id]['anzahl_raeume'] =  tree.xpath('//div[@class="hardfact rooms"]/text()')
except:
    print('id: ',id, ' no number of rooms(anzahl_raeume) could be retrieved')
try:
    data[id]['wohnflaeche'] =  tree.xpath('//div[@class="hardfact "]/text()')[3]
except:
    print('id: ',id, ' no living area (wohnflaeche) could be retrieved')
try:
    data[id]['grundstuecksflaeche'] =  tree.xpath('//div[@class="hardfact "]/text()')[5]
except:
    print('id: ',id, ' no lot size (grundstuecksflaeche) could be retrieved')
try:
    data[id]['beschreibung']= tree.xpath('//div[@class="section_content iw_right"]//span//text()')
except:
    print('id: ',id, ' no description (beschreibung) could be retrieved')
energieListe=["Energieausweistyp","Baujahr laut Energieausweis","Wesentliche EnergietrÃ¤ger","Endenergieverbrauch","Energieeffizienzklasse","GÃ¼ltigkeit"]#,"Wesentliche EnergietrÃ¤ger","Endenergieverbrauch'']

data = {}
data[id] = {}
for item in energieListe:
    # vollständige liste
    # tree.xpath('//div[@class="datarow clear"]//span//text()')
    path = '//div[@class="datarow clear" and contains(string(),"'+item+'")]//span//text()'
    data[id][item]= str(tree.xpath(path)[1])



tmp_text = tree.xpath('//div[@class="section_content iw_right"]/p//text()')
tmp_text

data[id]['Eigenschaften'] = tree.xpath('//ul[@class="textlist_icon_03 padding_top_none "]//span//text()')
data[id]['weitere_eigenschaften']



url = urls[1]
res = request.request("GET", url)
parser = etree.HTMLParser(recover=True)
tree = etree.HTML(res.data, parser)

id = get_id_from_url(url)
id
data[id]={
    'url':url,
    'title': tree.xpath('//title/text()')[0],
    'ort': tree.xpath('//div[@class="location"]/span/text()'),
    'merkmale':  tree.xpath('//div[@class="merkmale"]/text()'),
    'stadteilbewertung':  tree.xpath('//div[contains(@id,"divRating")]'),
    'kaufpreis': tree.xpath('//div[@class="hardfact"]/strong/strong/text()'),
    'anzahl_raeume': tree.xpath('//div[@class="hardfact rooms"]/text()')[0],
    'wohnflaeche': tree.xpath('//div[@class="hardfact "]/text()')[3],
    'grundstuecksflaeche': tree.xpath('//div[@class="hardfact "]/text()')[5],
    #'energielabel': tree.xpath('//div[@class="datatable energytable clear"]/div/span[@class="datalabel"]/text()')[0],
    #'energiemerkmale': tree.xpath('//div[@class="datatable energytable clear"]/div/span[@class="datacontent"]/text()')[0],
    #'energiemerkmale_checkbox':tree.xpath('//ul[contains(string(),"Haustyp")]//text()'),
    #'objektbeschreibung':tree.xpath('//div[contains(string(),"Objektbeschreibung")]//p/text()'),
}

(data)
data
