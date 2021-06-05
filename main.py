from scr import getargs as getarg
from scr import scraping as scrap
from scr.cleaning import *


def process_url(url):
    print("Processing : ", url)
    Exposes_text = scrap.get_project_ids(url=url)
    data = scrap.scrape_object_pages(Exposes_text)
    scrap.dump_to_json(data, url)
    print("Scraping completed")


if __name__ == "__main__":
    arguments = getarg.get_arguments()
    # for debugging:
    # arguments = (["muenchen"], False, True, True, False, True)
    start_urls = scrap.make_immowelt_urls(arguments)
    for url in start_urls:
        process_url(url)
    df = load_and_prepare_data()
    save_data_as_csv(df)
    remove_expose_files()
# my preferred scraping:
# hamburg norderstedt kaltenkirchen-holst ludwigslust-meckl schwerin wismar luebeck-hansestadt ratzeburg dortmund berlin
