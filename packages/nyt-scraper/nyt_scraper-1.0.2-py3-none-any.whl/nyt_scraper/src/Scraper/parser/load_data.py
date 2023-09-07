from bs4 import BeautifulSoup
from nyt_scraper.src import helpers
import json


def get_preload_data(response):
    return json.loads(
        helpers.parser_object_javascript(
            response.text.split("window.__preloadedData = ")[1]
            .split("</script>")[0]
            .rstrip(";")
        )
    )


def get_context(response, type_):
    r = [
        x.split("</script>")[0]
        for x in response.text.split(
            '<script data-rh="true" type="application/ld+json">'
        )
        if ',"@type":"{}"'.format(type_) in x
    ]
    if r:
        return r[0]


def get_next_data(response):
    return json.loads(
        helpers.parser_object_javascript(
            response.text.split('<script id="__NEXT_DATA__" type="application/json">')[
                1
            ]
            .split("</script>")[0]
            .rstrip(";")
        )
    )


def get_soup(response):
    return BeautifulSoup(response, "html.parser")
