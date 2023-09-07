from nyt_scraper.src.Scraper.parser import load_data
from nyt_scraper.src.Scraper.parser import attributes
from nyt_scraper.src.helpers import get_content_soup


def parser_search(response):
    sections = []
    types = []

    data = response.json()["data"]["search"]["hits"]
    totalEntries = data["totalCount"]
    entries = attributes.parser_entries(data["edges"])
    sections_ = data["metadata"]["facets"]["sections"]
    asset_types_ = data["metadata"]["facets"]["types"]
    pageInfo = data["pageInfo"]

    for section in sections_:
        sections.append(
            {
                "totalEntries": section["assetCount"],
                "uri": section["node"]["uri"],
                "name": section["node"]["name"],
                "displayName": section["node"]["displayName"],
            }
        )

    for asset_type in asset_types_:
        types.append(
            {"totalEntries": asset_type["assetCount"], "name": asset_type["assetType"]}
        )

    return {
        "entries": entries,
        "sections": sections,
        "types": types,
        "totalEntries": totalEntries,
        "pageInfo": pageInfo,
    }


def parser_person(response):
    data = response.json()["data"]["anyWork"]
    if data == None:
        return None  # person not found

    Name = data["displayName"]
    Biography = load_data.get_soup(data["legacyData"]["htmlBiography"]).text
    Photo = (
        attributes.parser_images(data["promotionalMedia"]["crops"])
        if data["promotionalMedia"]
        else None
    )
    Entries = attributes.parser_entries(data["stream"]["edges"])
    Social = attributes.parser_social(data["contactDetails"]["socialMedia"])
    pageInfo = data["stream"]["pageInfo"]
    totalEntries = data["stream"]["totalCount"]

    return {
        "name": Name,
        "biography": Biography,
        "photos": Photo,
        "entries": Entries,
        "social": Social,
        "totalEntries": totalEntries,
        "pageInfo": pageInfo,
    }


def parser_comments(response):
    return response.json()["results"]["comments"]


def parser_video(response):
    soup = load_data.get_soup(response.content)
    ID = soup.find("meta", {"name": "articleid"})["content"]
    files = load_data.get_preload_data(response)["initialState"]
    data = [v for k, v in files.items() if v.get("sourceId") == ID][0]

    url = data["url"]
    title = attributes.parser_title(data)
    summary = data["summary"]
    authors = (
        attributes.parser_authors(
            files[data["bylines"][0]["id"]]["renderedRepresentation"]
        )
        if data["bylines"]
        else None
    )
    language = files[data["language"]["id"]]["code"] if data["language"] else None
    published = data["firstPublished"]
    modified = data["lastModified"]
    section = (
        attributes.parser_section(files[data["section"]["id"]])
        if data["section"]
        else None
    )
    subsection = (
        attributes.parser_section(files[data["subsection"]["id"]])
        if data["subsection"]
        else None
    )
    duration = data["duration"]
    transcript = data["transcript"]
    renditions = attributes.parser_renditions(data["renditions"], files)
    keyword = [files[x["id"]]["vernacular"] for x in data["timesTags@filterEmpty"]]
    tags = [files[x["id"]]["displayName"] for x in data["timesTags@filterEmpty"]]

    return {
        "url": url,
        "title": title,
        "language": language,
        "authors": authors,
        "summary": summary,
        "published": published,
        "modified": modified,
        "section": section,
        "subsection": subsection,
        "duration": duration,
        "transcript": transcript,
        "renditions": renditions,
        "keyword": keyword,
        "tags": tags,
    }


def parser_slideshow(response):
    soup = load_data.get_soup(response.content)
    ID = soup.find("meta", {"name": "articleid"})["content"]

    try:
        files = load_data.get_preload_data(response)["initialState"]
        data = [v for k, v in files.items() if v.get("sourceId") == ID][0]
    except:
        files = None
        data = load_data.get_preload_data(response)["initialData"]["data"][
            "workOrLocation"
        ]

    url = data["url"]
    title = attributes.parser_title(data)
    summary = data["summary"]
    authors = attributes.parser_authors(
        get_content_soup(
            soup.find("meta", {"name": "byl", "data-rh": "true"}), "content"
        )
    )
    language = data["language"]["code"] if data["language"] else None
    published = data["firstPublished"]
    modified = data["lastModified"]
    section = attributes.parser_section(data["section"])
    subsection = attributes.parser_section(data["subsection"])
    name_tag = "timesTags@filterEmpty" if data["timesTags"] is None else "timesTags"

    if files:
        keyword = [files[x["id"]]["vernacular"] for x in data[name_tag]]
        tags = [files[x["id"]]["displayName"] for x in data[name_tag]]
    else:
        keyword = [x["vernacular"] for x in data[name_tag]]
        tags = [x["displayName"] for x in data[name_tag]]

    slides = [
        {
            "text": slide["caption"]["text"],
            "image": {
                "credit": slide["image"]["credit"],
                "url": attributes.parser_images(slide["image"]["crops"]),
            },
        }
        for slide in data["slides"]
    ]

    return {
        "url": url,
        "title": title,
        "language": language,
        "authors": authors,
        "published": published,
        "modified": modified,
        "section": section,
        "subsection": subsection,
        "keyword": keyword,
        "tags": tags,
        "summary": summary,
        "slides": slides,
    }


def parser_paidpost(response):
    data = load_data.get_preload_data(response)["initialData"]["data"]["paidPost"]
    soup = load_data.get_soup(response.content)

    url = data["url"]
    title = attributes.parser_title(data)
    summary = data["promotionalSummary"]
    language = get_content_soup(
        soup.find("meta", {"http-equiv": "Content-Language", "data-rh": "true"}),
        "content",
    )
    published = data["firstPublished"]
    modified = data["lastModified"]
    section = attributes.parser_section(data["section"])
    subsection = attributes.parser_section(data["subsection"])
    keyword = [x["vernacular"] for x in data["timesTags"]]
    tags = [x["displayName"] for x in data["timesTags"]]
    advertiser = data["advertiser"]
    advertiserUrl = data["advertiserUrl"]
    advertiserLogo = data["logoUrl"]

    return {
        "url": url,
        "title": title,
        "language": language,
        "published": published,
        "modified": modified,
        "section": section,
        "subsection": subsection,
        "summary": summary,
        "keyword": keyword,
        "tags": tags,
        "advertiser": advertiser,
        "advertiserUrl": advertiserUrl,
        "advertiserLogo": advertiserLogo,
    }


def parser_recipes(response):
    data = load_data.get_next_data(response)["props"]["pageProps"]["recipe"]

    url = data["fullUrl"]
    title = attributes.parser_title(data)
    summary = data["topnote"]
    authors = [
        {"name": author["name"], "url": "https://cooking.nytimes.com" + author["link"]}
        for author in data["contentAttribution"]["primaryByline"]["authors"]
    ]
    adapted = [
        {"name": author["name"], "url": "https://cooking.nytimes.com" + author["link"]}
        for author in data["contentAttribution"]["secondaryByline"]["authors"]
    ]
    image = {"link": data["image"]["src"]["card"], "credit": data["image"]["credit"]}
    time = data["time"]
    rating = data["ratings"]["avgRating"]
    ratingCount = data["ratings"]["numRatings"]
    relatedArticles = [
        {
            "name": article["headline"],
            "author": article["byline"],
            "url": article["url"],
        }
        for article in data["relatedArticles"]
    ]
    relatedGuides = [
        {
            "author": guide["author"],
            "image": guide["image"]["src"]["card"],
            "title": guide["title"],
            "url": "https://cooking.nytimes.com" + guide["url"],
        }
        for guide in data["relatedGuides"]
    ]
    nutritionalInformation = [
        {
            "text": nutritional["header"],
            "information": nutritional["description"].split("; "),
            "source": nutritional["source"],
        }
        for nutritional in data["nutritionalInformation"]
    ]
    yield_ = data["recipeYield"]
    ingredients = data["ingredients"]
    steps = data["steps"]
    tips = data["tips"]
    tags = [
        {"name": tag["name"], "url": "https://cooking.nytimes.com" + tag["path"]}
        for tag in data["tags"]
    ]

    return {
        "url": url,
        "title": title,
        "authors": authors,
        "summary": summary,
        "adapted": adapted,
        "image": image,
        "time": time,
        "rating": rating,
        "ratingCount": ratingCount,
        "relatedArticles": relatedArticles,
        "relatedGuides": relatedGuides,
        "nutritionalInformation": nutritionalInformation,
        "yield_": yield_,
        "ingredients": ingredients,
        "steps": steps,
        "tips": tips,
        "tags": tags,
    }


def parser_audio(response):
    soup = load_data.get_soup(response.content)
    data = load_data.get_preload_data(response)["initialData"]["data"]["workOrLocation"]
    url = data["url"]
    title = attributes.parser_title(data)
    summary = data["summary"]
    published = data["firstPublished"]
    transcript = data["audioTranscript"]
    fileUrl = data["fileUrl"]
    section = attributes.parser_section(data["section"]) if data["section"] else None
    subsection = (
        attributes.parser_section(data["subsection"]) if data["subsection"] else None
    )
    language = get_content_soup(
        soup.find("meta", {"http-equiv": "Content-Language", "data-rh": "true"}),
        "content",
    )

    return {
        "url": url,
        "title": title,
        "language": language,
        "summary": summary,
        "transcript": transcript,
        "published": published,
        "fileUrl": fileUrl,
        "section": section,
        "subsection": subsection,
    }


def parser_interactive(response):
    soup = load_data.get_soup(response.content)
    try:
        data = load_data.get_preload_data(response)["interactiveConfig"]["interactive"]
    except:
        data = {"url": response.url, "title": soup.find("h1").text, "summary": None}

    url = data["url"]
    title = attributes.parser_title(data)
    summary = data["summary"]
    section = (
        attributes.parser_section(data["section"]) if data.get("section") else None
    )
    subsection = (
        attributes.parser_section(data["subsection"])
        if data.get("subsection")
        else None
    )
    authors = attributes.parser_authors(
        get_content_soup(
            soup.find("meta", {"name": "byl", "data-rh": "true"}), "content"
        )
    )
    published = get_content_soup(
        soup.find("meta", {"property": "article:published_time", "data-rh": "true"}),
        "content",
    )
    modified = get_content_soup(
        soup.find("meta", {"property": "article:modified_time", "data-rh": "true"}),
        "content",
    )
    language = get_content_soup(
        soup.find("meta", {"http-equiv": "Content-Language", "data-rh": "true"}),
        "content",
    )

    return {
        "url": url,
        "title": title,
        "language": language,
        "authors": authors,
        "summary": summary,
        "published": published,
        "modified": modified,
        "section": section,
        "subsection": subsection,
    }


def parser_article(response):
    try:
        data = load_data.get_preload_data(response)["initialData"]["data"]
    except:
        return None

    if data.get("article"):
        data = data["article"]
    elif data.get("explainerAsset"):
        data = data["explainerAsset"]
    else:
        raise Exception("Error inesperado")

    url = data["url"]
    title = attributes.parser_title(data)
    summary = data["summary"]
    language = data["language"]["code"] if data["language"] else None
    authors = (
        attributes.parser_authors(data["bylines"]) if data.get("bylines") else None
    )
    published = data["firstPublished"]
    modified = data["lastModified"]
    section = attributes.parser_section(data["section"])
    subsection = attributes.parser_section(data["subsection"])
    alteration = (
        [
            {"text": endum["body"]["text"], "date": endum["publicationDate"]}
            for endum in data["addendums"]
        ]
        if data.get("addendums")
        else None
    )

    return {
        "url": url,
        "title": title,
        "language": language,
        "authors": authors,
        "published": published,
        "modified": modified,
        "section": section,
        "subsection": subsection,
        "summary": summary,
        "alteration": alteration,
    }


def get(func, response):
    return func(response)
