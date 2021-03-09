import urllib3
from lxml import etree
import re

test = '2021-02-28-hamburg-haeuser-kaufen.txt'
#test = '2021-02-28-hamburg-wohnungen-kaufen.txt'
#test = '2021-02-28-ludwigslust-meckl-haus-mieten.txt'

def prepare_urls(filename):
    """read text_file containing expose-ids, return list of urls"""
    with open(filename, "r") as f:
        exposes = f.read()
    exposes = exposes.split(sep=" ")
    url_root = 'https://www.immowelt.de/expose/'
    return [url_root+a for a in exposes]

urls =prepare_urls(test)

def get_id_from_url(url):
    """Gibt die Objekt-ID aus einer url zurück"""
    id = re.search(r'(?<=expose\/).*',url)
    return id.group(0)


#----------------------Kompletter Scraping Vorgang für eine Objekt-Seite
url = urls[0]
url
#url='https://www.immowelt.de/expose/2xcl64z'

res = request.request("GET", url)
parser = etree.HTMLParser(recover=True, encoding="utf-8")
tree = etree.HTML(res.data, parser)

# hiermit wird die Test-Seite gedownloadet.
with open("beispiel_haus_kaufen.html",'a') as f:
    f.write(res.data.decode('utf-8'))

id = get_id_from_url(url)
data = {}
data[id] = {}
data[id]['url'] = url
xpath_patterns = {
'title':'//title/text()',
'ort':'//div[@class="location"]/span/text()',
'merkmale':'//div[@class="merkmale"]/text()',
'stadteilbewertung':'//div[contains(@id,"divRating")]',
'preis':'//div[@class="hardfact"]/strong/strong/text()',
'anzahl_raeume':'//div[@class="hardfact rooms"]/text()',
'wohnflaeche':'//div[@class="hardfact "]/text()',
'grundstuecksflaeche':'//div[@class="hardfact "]/text()',
'weitere_eigenschaften':'//ul[@class="textlist_icon_03 padding_top_none "]//span//text()',
'beschreibung':'//div[@class="section_content iw_right"]/p//text()',
}
for key, xpath_pattern in xpath_patterns.items():
    try: # falls kein Treffer in xpath
        uncleanContent = tree.xpath(xpath_pattern)
    except:
        continue
    #print(key)
    data[id][key]  = uncleanContent

#-----manche xpath - Element sind Listen und man benötigt nur wenige Elemente
for key in ['title','ort','merkmale','anzahl_raeume','preis']:
    data[id][key] = data[id][key][0]

data[id]['wohnflaeche'] = data[id]['wohnflaeche'][3]
data[id]['grundstuecksflaeche'] = data[id]['grundstuecksflaeche'][5]

[key for key in data[id].keys()]

for key, value in data[id].items():
    try:
        data[id][key] = clean_whitespace(data[id][key] )
    except:
        continue

data
#---- die Energiefelder werden direkt ausgelesen und das geht am einfachsten über eine for loop.
energieListe=["Energieausweistyp","Baujahr laut Energieausweis","Wesentliche Energieträger","Endenergieverbrauch","Energieeffizienzklasse","Gültigkeit"]#,"Wesentliche EnergietrÃ¤ger","Endenergieverbrauch'']
for item in energieListe:
    # vollständige liste
    # tree.xpath('//div[@class="datarow clear"]//span//text()')

    try:
        path = '//div[@class="datarow clear" and contains(string(),"'+item+'")]//span//text()'
        data[id][item]= str(tree.xpath(path)[1])
        print(item)
    except:
        continue

# ------- Bereinigung der Felder um \r\n und whitespaces
# es gibt kurze, nur ein text-Element umfassende zu reinigende Elemente
# und lange, listen von texten. Die beiden werden nun automatisch unterschieden und
# jeweils entsprechend gereinigt.

tmp_lang = tree.xpath('//div[@class="section_content iw_right"]/p//text()')
tmp_lang


tmp_kurz = data[id]['wohnflaeche']
tmp_kurz
#--- check of checktype funktioniert
checktype(tmp_lang)
checktype(tmp_kurz)

def checktype(obj):
    """Prüfen, ob es sich um eine Liste von Strings handelt
    basiert auf https://stackoverflow.com/questions/18495098/python-check-if-an-object-is-a-list-of-strings"""
    return bool(obj) and all(isinstance(elem, str) for elem in obj) and not all(len(elem)==1 for elem in obj)

def clean_whitespace(tmp_text):
    """Entfernt \r und \n und leere Zeilen sowohl aus
    Listen von Text als auch von Textteilen."""

    if checktype(tmp_text): # liste von str
        print("langer text")
        tmp_res = []
        for line in tmp_text:
            line_clean = re.sub(r'\r\n[ ]*','',line) # preceeding \r\n and whitespaces
            len_line = len(line_clean)
            if len_line==0 or line_clean==" "*len_line:
                continue
            tmp_res.append(line_clean)
        return tmp_res
    else: # nur ein str
        return re.sub(r'\r\n[ ]*|[ ]*$','',tmp_text)

data
clean_whitespace(tmp_lang)

clean_whitespace(data[id]['wohnflaeche'])
