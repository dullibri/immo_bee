from . import getargs as getarg
from . import scraping as scrap
from .cleaning import *


def process_url(url):
    print("Processing : ", url)
    Exposes_text = scrap.get_project_ids(url=url)
    data = scrap.scrape_object_pages(Exposes_text)
    scrap.dump_to_json(data, url)
    print("Scraping completed")


def bee(rent=True, buy=True, house=True, appartment=True, locations=None):

    if locations:

        class inputs:
            rent = rent
            buy = buy
            house = house
            appartment = appartment
            locations = locations

        arguments = inputs
    else:
        arguments = getarg.get_arguments()

    start_urls = scrap.make_immowelt_urls(arguments)
    for url in start_urls:
        process_url(url)
    df = load_and_prepare_data()
    if locations:
        return df
    else:
        save_data_as_csv(df)
        remove_expose_files()


if __name__ == "__main__":
    bee()

# my preferred scraping:
# hamburg landkreis-segeberg kaltenkirchen-holst norderstedt ludwigslust-meckl schwerin wismar luebeck-hansestadt ratzeburg dortmund berlin
