from main import *
from datetime import date
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
url = 'https://www.immowelt.de/liste/berlin/wohnungen/kaufen'

city = "berlin"
flat_house = "wohnungen"
rent_buy = "kaufen"
url = 'https://www.immowelt.de/liste/'+city+'/'+flat_house+'/'+rent_buy
print(url)

driver = get_driver()
start_soup = soup_get(url, driver)


hrefs = href_finder(start_soup)
hrefs
num_pages = n_pages(hrefs)
print(num_pages)

href_extr(hrefs)
projekt_finder(hrefs)
