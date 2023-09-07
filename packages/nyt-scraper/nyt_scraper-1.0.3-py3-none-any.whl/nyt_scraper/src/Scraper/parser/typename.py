from nyt_scraper.src.Scraper.parser.general import *
from nyt_scraper.src.exceptions import *


def detect_article(url):
    key = url.split("nytimes.com/")[1].split("/")[0]

    if (
        key.isdigit()
        and len(key) == 4
        and int(key) > 1800
        or key == "article"
        or key == "live"
    ):
        return True


def get(url):
    if "/video/" in url:
        return parser_video, "video"
    elif "/slideshow/" in url:
        return parser_slideshow, "slideshow"
    elif "/recipes/" in url:
        return parser_recipes, "recipe"
    elif "/interactive/" in url:
        return parser_interactive, "interactive"
    elif "/by/" in url:
        return parser_person, "person"
    elif "/audio/" in url:
        return parser_audio, "audio"
    elif "/paidpost/" in url:
        return parser_paidpost, "paidpost"
    elif detect_article(url):
        return parser_article, "article"
    elif "/newsgraphics/" in url:
        return NewsGraphicsScrapingNotAllowed, False
    elif "/wirecutter/" in url:
        return WirecutterScrapingNotAllowed, False
    else:
        return PageNotAllowed, False


def check(url, typename):
    func, type_ = get(url)

    if type_ != typename:
        if type_ == False:
            raise func()
        else:
            message = "You are using the get_{}() function and the url is a {}. You must use get_{}()".format(
                typename, type_, type_
            )
            raise Exception(message)
