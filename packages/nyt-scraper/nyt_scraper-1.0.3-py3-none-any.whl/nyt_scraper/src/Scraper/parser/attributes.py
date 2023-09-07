from nyt_scraper.src import helpers
import re
from urllib.parse import urljoin
import base64


def parser_images(crops):
    images = []

    for crop in crops:
        for rendition in crop["renditions"]:
            images.append(
                {
                    "url": rendition["url"],
                    "name": rendition["name"],
                    "typename": rendition["__typename"],
                    "width": rendition.get("width"),
                    "height": rendition.get("height"),
                }
            )

    return images


def parser_renditions(renditions_, files):
    renditions = []
    for x in renditions_:
        data = files[x["id"]]
        del data["__typename"]
        url = data["url"]
        data["type_"] = data["type"]
        del data["type"]

        if url.endswith(".m3u8"):
            renditions.extend(helpers.get_info_data_m3u8(data))
        else:
            renditions.append(data)
    return renditions


# By Robin Stein, Caroline Kim, Malachy Browne and Whitney Hurst


def parser_authors_text(text):  # By Axel Boada and Ian Corry for The New York Times
    if text == None:
        return
    text = text.lower()

    if text.startswith("by "):
        text = text[3:]

    text = text.split(" for ")[0]
    names = [{"name": x} for x in re.split(r", | and ", text)]
    return names


def parser_authors(bylines):
    authors = []

    if bylines:
        if isinstance(bylines, str):
            return parser_authors_text(bylines)

        elif bylines[0].get("creators") or bylines[0].get("creatorSnapshots"):
            for author in (
                bylines[0]["creators"]
                if bylines[0].get("creators")
                else bylines[0]["creatorSnapshots"]
            ):
                authors.append(
                    {
                        "name": author["displayName"],
                        "photos": parser_images(author["promotionalMedia"]["crops"])
                        if author.get("promotionalMedia")
                        else None,
                    }
                )
        else:
            return parser_authors_text(bylines[0]["renderedRepresentation"])
    return authors


def get_uri(ID):
    return base64.b64decode(ID)[8:]


def parser_section(section):
    return (
        {
            "name": section["name"],
            "displayName": section.get("displayName"),
            "url": urljoin("https://www.nytimes.com/", section["url"])
            if section.get("url")
            else None,
            "uri": section.get("uri", get_uri(section["id"])),
        }
        if section
        else None
    )


def parser_social(social):
    return [
        {"type": contact["type"], "account": contact["account"]} for contact in social
    ]


def parser_title(entry):
    if entry.get("promotionalHeadline"):
        return entry["promotionalHeadline"]

    elif entry.get("creativeWorkHeadline"):
        return entry["creativeWorkHeadline"]["default"]

    elif entry.get("title"):
        return entry["title"]

    else:
        return entry["headline"]["default"]


def parser_entries(entries):
    new_entries = []
    from pprint import pprint

    for c, edge in enumerate(entries):
        if "node" in edge:
            edge = edge["node"]
            if isinstance(edge, dict) and "node" in edge:
                edge = edge["node"]

        if edge:
            new_entries.append(
                {
                    "url": edge["url"],
                    "published": edge["firstPublished"],
                    "modified": edge.get("lastModified"),
                    "title": parser_title(edge),
                    "summary": edge["summary"]
                    if edge.get("summary")
                    else edge.get("creativeWorkSummary"),
                    "authors": parser_authors(edge["bylines"]),
                }
            )

    return new_entries
