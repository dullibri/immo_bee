import argparse


def get_arguments():
    """Collects the commandline arguments.

    Returns:
        arguments: (locations, rent, buy, house, appartment),
                locations [list]: strings of locations to be scraped.
                rent [boolean], buy [boolean], both are mutually exclusive.
                house [boolean], rent [boolean], both are mutually exclusive.
    """
    description = """
    This is a scraper for immowelt.de. You need to supply the name(s) of the 
    location(s) you want to scrape. If you do not specify anything more, it will 
    return an excel sheet with the houses and appartments on offer or for rent.

    {Not yet implemented: You can also specify rent/buy or houses/appartments reducing the 
    result respectively.}
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

    args = parser.parse_args()
    locations = args.locations[0]
    locations_formated = ", ".join([loc.capitalize() for loc in locations])
    buy, rent, appartment, house, verbose = (
        args.buy,
        args.rent,
        args.appartment,
        args.house,
        args.verbose,
    )
    if args.verbose:
        print(60 * "-")
        print("\nLocations that will be scraped:", locations_formated)
        if appartment:
            print("\nOnly appartments will be scraped.")
        elif house:
            print("\nOnly houses will be scraped.")
        if buy:
            print("Only objects for sale will be included.")
        if rent:
            print("Only objects for rent will be included.")
        if not (appartment + house + rent + buy):
            print("\nRent and buy offers for houses and appartments will be scraped.")
        print("\n" + 60 * "-")
    return (locations, rent, buy, house, appartment, verbose)


if __name__ == "__main__":
    get_arguments()
