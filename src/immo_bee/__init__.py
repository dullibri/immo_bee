from numpy import busday_count

from . import getargs as getarg
from . import scraping as scrap
from .cleaning import *


def process_url(url, log_path="geckodriver.log"):
    print("Processing : ", url)
    Exposes_text = scrap.get_project_ids(url=url, log_path=log_path)
    data = scrap.scrape_object_pages(Exposes_text)
    scrap.dump_to_json(data, url)
    print("Scraping completed")


def bee(locations=None, rent=True, buy=True, house=True, appartment=True):
    """Scrapes locations from immowelt.de and returns a dataframe of the
    preprocessed data. Default: all houses and appartments and all offerings
    for rent and sale are included.

    If only house/appartment or rent/buy are
    specified the other option is excluded. For example, if house is set to
    True, appartment is set to False. If rent is set to True, buy is set to
    False and vice versa.

    Args:
        locations (list of strings, optional): . Defaults to None.
        rent (bool, optional): include housing for rent. Defaults to True.
        buy (bool, optional): include housing for sale. Defaults to True.
        house (bool, optional): include houses. Defaults to True.
        appartment (bool, optional): include appartments. Defaults to True.

    Returns:
        pandas.DataFrame: All offerings preprocessed.
    """
    print(locations)
    if locations:

        class inputs:
            pass

        arguments = inputs()
        arguments.locations = list()
        arguments.locations.append(locations)
        arguments.rent = rent
        arguments.buy = buy
        arguments.house = house
        arguments.appartment = appartment

    else:
        arguments = getarg.get_arguments()

    start_urls = scrap.make_immowelt_urls(arguments)
    for url in start_urls:
        process_url(url, arguments.logpath)
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
