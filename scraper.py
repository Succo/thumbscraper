import json
import requests
import sys

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from lxml import etree


def requests_retry_session(retries=3,
                           backoff_factor=0.3,
                           status_forcelist=(500, 502, 504),
                           session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_data(input_file):
    try:
        # Parsing the input json
        with open(input_file) as f:
            data = json.load(f)

        return data
    except Exception as e:
        sys.exit(e)


def scrape(base_url, auth, data):
    # Initializing the loop
    try:
        content = requests_retry_session().get(base_url, auth=auth)
    except Exception as e:
        sys.exit(e)
    # Counter of pages seen so far
    page = 0
    # Id of the page we are at
    id = "0"

    while True:
        values = data[id]
        # I'm using lxml.etree to parse the html
        tree = etree.HTML(content.text)
        # This is comparing that the test query returns the expected result
        if tree.xpath(values['xpath_test_query']) != \
           values['xpath_test_result']:
            print("ALERT - Can’t move to page {}: page {} link has been \
    malevolently tampered with!!"
                  .format(page+1, page))
            # Quit the loop on error case
            break
        # Getting the next url
        path = tree.xpath(values['xpath_button_to_click'])[0].attrib['href']
        url = base_url+path
        # Loading the next page and updating all the variables used in the loops
        try:
            content = requests_retry_session().get(url, auth=auth)
        except Exception as e:
            sys.exit(e)
        page += 1
        id = values['next_page_expected']
        # Printing that the page is correct
        print("Move to page {}".format(page))


if __name__ == "__main__":
    # Constant of the exercise
    base_url = 'https://yolaw-tokeep-hiring-env.herokuapp.com/'
    user = 'Thumb'
    password = 'Scraper'
    input_file = 'thumbscraper_input_tampered.hiring-env.json'

    data = get_data(input_file)
    scrape(base_url, (user, password), data)
