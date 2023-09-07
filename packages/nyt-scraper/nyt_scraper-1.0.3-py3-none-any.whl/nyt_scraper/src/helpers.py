import re
from bs4 import BeautifulSoup
from datetime import datetime
from m3u8 import M3U8
import requests
from nyt_scraper.src.exceptions import *

get_content_soup = (
    lambda soup, x: soup.get(x) if soup.get(x) else None if soup else None
)


def get_info_data_m3u8(x):
    response = requests.get(x["url"])
    m3u8_master = M3U8(response.text)
    renditions = []

    for playlist in m3u8_master.playlists:
        width, height = playlist.stream_info.resolution
        url = "{}/{}".format(x["url"].rsplit("/", 1)[0], playlist.uri)
        x["width"] = width
        x["height"] = height
        x["url"] = url
        renditions.append(x.copy())
    return renditions


def format_timestamp(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%d de %B de %Y, %H:%M:%S")


def get_text(html):
    return BeautifulSoup(html, "html.parser").text


def parser_object_javascript(object):
    return re.sub(r'("\s*:\s*)undefined(\s*[,}])', "\\1null\\2", object)


def make_filterQuery(type_, section):
    if type_ and section:
        return f"{section} AND {type_}"
    elif type_:
        return type_
    elif section:
        return section
    else:
        return ""


def format_sort(sort):
    sort = sort.lower()
    if sort == "best" or sort == "oldest" or sort == "newest":
        return sort
    return "best"


def format_data_section(data):
    if isinstance(data, str):
        data = [data]
    elif isinstance(data, list):
        pass
    else:
        try:
            if data.name:
                data = [data.name]
            elif data.uri:
                data = [data.uri]
        except:
            raise InvalidSection("Invalid Section")

    formatted_data_section = []

    for data_section in data:
        for type_ in ("section", "subsection"):
            for key in ("name", "displayName", "uri"):
                formatted_data_section.append(
                    '({}.{}: "{}")'.format(type_, key, data_section)
                )

    combined_string = " OR ".join(formatted_data_section)
    final_query = f"({combined_string})"
    return final_query


def format_data_types(data, key="section_uri"):
    if isinstance(data, str):
        data = [data]

    formatted_data_types = ['({}: "{}")'.format(key, data_type) for data_type in data]
    combined_string = " OR ".join(formatted_data_types)
    final_query = f"({combined_string})"
    return final_query
