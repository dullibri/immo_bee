import os

from numpy import busday_count

from . import getargs as getarg
from . import scraping as scrap
from .cleaning import *


def process_url(url, arguments):
    print("Processing : ", url)
    expose_ids = scrap.get_project_ids(url=url)
    data = scrap.scrape_object_pages(expose_ids)
    s3_bucket = arguments.s3_bucket if len(arguments.s3_bucket) > 0 else None
    print(s3_bucket)
    if s3_bucket:
        scrap.dump_to_s3(s3_bucket, data, url)
    else:
        scrap.dump_to_json(data, url, arguments)
    print("Scraping completed")


def bee(
    locations=None,
    rent=True,
    buy=True,
    house=True,
    appartment=True,
    data_folder="data",
    s3_bucket="",
):
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
        house (bool, optional): include houses. Defaults to True.
        appartment (bool, optional): include appartments. Defaults to True.
        data_folder (string, optional): folder where to dump jsons. Defaults to "data".
        s3_bucket (str, optional): name of s3 bucket to put the data as json to.

    Returns:
        pandas.DataFrame: All offerings preprocessed.
    """
    if locations:
        print(f"Immobee is run as module, scraping: {locations}")

        class inputs:
            pass

        arguments = inputs()
        arguments.locations = list()
        arguments.locations.append(locations)
        arguments.rent = rent
        arguments.buy = buy
        arguments.house = house
        arguments.appartment = appartment
        arguments.data_folder = data_folder
        arguments.s3_bucket = s3_bucket

    else:
        arguments = getarg.get_arguments()
        print(f"Immobee is run from commandline, scraping: {arguments.locations}")

    start_urls = scrap.make_immowelt_urls(arguments)
    for url in start_urls:
        process_url(url, arguments)

    df = load_and_prepare_data(arguments)

    if locations:
        return df
    else:
        save_data(df, arguments.data_folder)


if __name__ == "__main__":
    bee()
