import argparse

description="""
This is a scraper for immowelt.de. You need to supply the name(s) of the 
location(s) you want to scrape. If you do not specify anything more, it will 
return an excel sheet with the houses and appartments on offer or for rent.

You can also specify rent/buy or houses/appartments reducing the 
result respectively.
"""
parser = argparse.ArgumentParser(description=description)

parser.add_argument("locations",action="append",nargs="*",help="locations for which you like to scrape data")
parser.add_argument("-b","--buy", help="only objects for sale will be returned",action="store_true")
parser.add_argument("-r","--rent",help="only objects for rent will be returned",action="store_true")
parser.add_argument("-ap","--appartments",help="only appartments will be returned",action="store_true")
parser.add_argument("-ho","--houses",help="only houses will be returned",action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()
    locations = args.locations[0]
    print("locations ", locations)
    print("type ", args.appartments)