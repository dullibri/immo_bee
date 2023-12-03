import argparse


def get_arguments():

    description = """
    This is a scraper for immowelt.de. You need to supply the name(s) of the 
    location(s) you want to scrape. If you do not specify anything more, it will 
    return an excel sheet with the houses and appartments on offer or for rent.

    You can also specify rent/buy or houses/appartments reducing the 
    result respectively.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "locations",
        action="append",
        nargs="*",
        help="locations for which you like to scrape data",
    )
    # need to be added:
    group_type = parser.add_mutually_exclusive_group()
    group_type.add_argument(
        "-b",
        "--buy",
        help="only objects for sale will be returned",
        action="store_true",
    )
    group_type.add_argument(
        "-r",
        "--rent",
        help="only objects for rent will be returned",
        action="store_true",
    )
    group_object = parser.add_mutually_exclusive_group()
    group_object.add_argument(
        "-ap",
        "--appartment",
        help="only appartments will be returned",
        action="store_true",
    )
    group_object.add_argument(
        "-ho", "--house", help="only houses will be returned", action="store_true"
    )
    parser.add_argument("-v", "--verbose", action="store_true")

    parser.add_argument(
        "-df",
        "--data-folder",
        help="local directory path to store the scraped data, will be created if it does not exist.",
        default="data",
    )

    parser.add_argument(
        "-pl",
        "--path-geckodriver-log",
        help="path to store the geckodriver logfile",
        default=".",
    )

    args = parser.parse_args()
    locations = args.locations[0]
    locations_formated = ", ".join([loc.capitalize() for loc in locations])

    if args.verbose:
        print(60 * "-")
        print("\nLocations that will be scraped:", locations_formated)
        if args.appartment:
            print("\nOnly appartments will be scraped.")
        elif args.house:
            print("\nOnly houses will be scraped.")
        if args.buy:
            print("Only objects for sale will be included.")
        if args.rent:
            print("Only objects for rent will be included.")
        if not (args.appartment + args.house + args.rent + args.buy):
            print("\nRent and buy offers for houses and appartments will be scraped.")
        print("\n" + 60 * "-")
    return args


if __name__ == "__main__":
    get_arguments()
