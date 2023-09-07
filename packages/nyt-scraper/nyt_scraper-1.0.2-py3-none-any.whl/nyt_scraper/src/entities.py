from nyt_scraper.src.Scraper.scraper import Scraper
from nyt_scraper.src.Scraper import download
from nyt_scraper.src.Scraper.parser.typename import detect_article


class _Array:
    def __init__(self, clase=None, elements=None):
        if elements is None:
            elements = []
        self.list = [clase(**x) for x in elements]

    def __append(self, clase, element):
        self.list.append(clase(**element))

    def __getitem__(self, key):
        try:
            return self.list[key]
        except:
            message = "IndexError: list index out of range."
            raise IndexError(message)

    def __len__(self):
        return len(self.list)


class Section:
    def __init__(self, uri, name, displayName, url=None, totalEntries=None):
        self.uri = uri
        self.name = name
        self.displayName = displayName
        self.url = url
        self.totalEntries = totalEntries

    def __repr__(self):
        return f"Section(uri, url, name, displayName, totalEntries)"


class Sections(_Array):
    def __init__(self, sections=None):
        if sections is None:
            sections = []
        super().__init__(clase=Section, elements=sections)
        self.sections = self.list

    def find(self, uri=None, name=None, displayName=None, url=None):
        for section in self.sections:
            if (
                (uri is None or section.uri == uri)
                and (name is None or section.name == name)
                and (displayName is None or section.displayName == displayName)
                and (url is None or section.url == url)
            ):
                return section
        return None

    def __repr__(self):
        return f"Sections({len(self.sections)} section)"


class Subsection(Section):
    def __repr__(self):
        return f"Subsection(uri, url, name, displayName, totalEntries)"


class Subsections:
    def __init__(self, subsections=None):
        if subsections is None:
            subsections = []
        super().__init__(clase=Subsections, elements=subsections)
        self.subsections = self.list

    def find(self, uri=None, name=None, displayName=None, url=None):
        for subsection in self.subsections:
            if (
                (uri is None or subsection.uri == uri)
                and (name is None or subsection.name == name)
                and (displayName is None or subsection.displayName == displayName)
                and (url is None or subsection.url == url)
            ):
                return subsection
        return None

    def __repr__(self):
        return f"Subsections({len(self.subsections)} subsection)"


class Type:
    def __init__(self, name, totalEntries):
        self.name = name
        self.totalEntries = totalEntries

    def __repr__(self):
        return f"Type(name, totalEntries)"


class Types(_Array):
    def __init__(self, types=None):
        if types is None:
            types = []
        super().__init__(clase=Type, elements=types)
        self.types = self.list

    def find(self, name=None):
        for type_ in self.types:
            if name is None or type_.name == name:
                return type_
        return None

    def __repr__(self):
        return f"Types({len(self.types)} types)"


class Rendition:
    def __init__(self, url, width, height, type_, bitrate, aspectRatio):
        self.url = url
        self.width = width
        self.height = height
        self.type = type_
        self.bitrate = bitrate
        self.aspectRatio = aspectRatio

    def download(self, path):
        download.video(self.url, path)

    def __repr__(self):
        return f"Rendition(url, width, height, type, bitrate, aspectRatio)"


class Renditions(_Array):
    def __init__(self, renditions=None):
        if renditions is None:
            renditions = []
        super().__init__(clase=Rendition, elements=renditions)
        self.renditions = self.list
        self.__find_best_video()

    def download(self, path):
        download.video(self.__best_file.url, path)
        return True

    def find(self, width=None, height=None, type_=None):
        for rendition in self.renditions:
            if (
                (width is None or rendition.width == width)
                and (height is None or rendition.height == height)
                and (
                    type_ is None or rendition.type == type_ or type_ in rendition.type
                )
            ):
                return rendition
        return None

    def __find_best_video(self):
        self.__best_file = None
        mejor_resolucion = 0

        for archivo in self.renditions:
            url = archivo.url
            if url.endswith(".mp4"):
                resolucion = archivo.width * archivo.height
                if resolucion > mejor_resolucion:
                    mejor_resolucion = resolucion
                    self.__best_file = archivo

    def __repr__(self):
        return f"Renditions({len(self.renditions)} renditions)"


class Search:
    def __init__(self, entries, sections, types, pageInfo, totalEntries, query):
        self.entries = Entries(entries)
        self.sections = Sections(sections)
        self.types = Types(types)
        self.totalEntries = totalEntries
        self.__pageInfo = pageInfo
        self.__query = query

    def __cursor_next_page(self):
        if self.__pageInfo["hasNextPage"]:
            return self.__pageInfo["endCursor"]

    def __cursor_previus_page(self):
        if self.__pageInfo["hasPreviousPage"]:
            return self.__pageInfo["startCursor"]

    def next(self):
        cursor = self.__cursor_next_page()

        if len(self) >= 1000:
            raise Exception("Has excedido el limite de next de este search.")

        if cursor:
            self.__query["cursor"] = cursor
            response = Scraper()._Scraper__search(**self.__query)
            self.__pageInfo = response["pageInfo"]
            [
                self.entries._Array__append(clase=_typename(x["url"]), element=x)
                for x in response["entries"]
            ]
            return self.entries[-len(response["entries"]) :]

    def __len__(self):
        return len(self.entries)

    def __repr__(self):
        return f"Search(entries, sections, types, totalEntries)"


class Interactive:
    def __init__(
        self,
        url,
        title=None,
        language=None,
        authors=None,
        summary=None,
        published=None,
        modified=None,
        section=None,
        subsection=None,
    ):
        self.type = "interactive"
        self.url = url
        self.__title = title
        self.__language = language
        self.__authors = Persons(authors) if authors else None
        self.__summary = summary
        self.__published = published
        self.__modified = modified
        self.__section = Section(**section) if section else None
        self.__subsection = Subsection(**subsection) if subsection else None
        self.__scrape = False

    def __getattr__(self, name):
        return None

    def __scrape_(self):
        if self.__scrape is False:
            p = Scraper()._Scraper__get_interactive(self.url)
            self.__scrape = True

            if p:
                self.__title = p["title"]
                self.__language = p["language"]
                self.__authors = Persons(p["authors"])
                self.__summary = p["summary"]
                self.__published = p["published"]
                self.__modified = p["modified"]
                self.__section = Section(**p["section"]) if p["section"] else None
                self.__subsection = (
                    Section(**p["subsection"]) if p["subsection"] else None
                )

    @property
    def title(self):
        if self.__title is None:
            self.__scrape_()
        return self.__title

    @property
    def language(self):
        if self.__language is None:
            self.__scrape_()
        return self.__language

    @property
    def authors(self):
        if self.__authors is None:
            self.__scrape_()
        return self.__authors

    @property
    def summary(self):
        if self.__summary is None:
            self.__scrape_()
        return self.__summary

    @property
    def published(self):
        if self.__published is None:
            self.__scrape_()
        return self.__published

    @property
    def modified(self):
        if self.__modified is None:
            self.__scrape_()
        return self.__modified

    @property
    def section(self):
        if self.__section is None:
            self.__scrape_()
        return self.__section

    @property
    def subsection(self):
        if self.__subsection is None:
            self.__scrape_()
        return self.__subsection

    def __repr__(self):
        return f"Interactive(type, url, title, language, authors, summary, published, modified, section, subsection)"


class Audio:
    def __init__(
        self,
        url,
        title=None,
        language=None,
        summary=None,
        transcript=None,
        published=None,
        fileUrl=None,
        section=None,
        subsection=None,
    ):
        self.type = "audio"
        self.url = url
        self.__title = title
        self.__language = language
        self.__summary = summary
        self.__transcript = transcript
        self.__published = published
        self.__fileUrl = fileUrl
        self.__section = Section(**section) if section else None
        self.__subsection = Subsection(**subsection) if subsection else None
        self.__scrape = False

    def __getattr__(self, name):
        return None

    def download(self, path):
        download.audio(self.fileUrl, path)
        return True

    def __scrape_(self):
        if self.__scrape is False:
            p = Scraper()._Scraper__get_audio(self.url)
            self.__scrape = True

            if p:
                self.__title = p["title"]
                self.__language = p["language"]
                self.__summary = p["summary"]
                self.__transcript = p["transcript"]
                self.__published = p["published"]
                self.__fileUrl = p["fileUrl"]
                self.__section = Section(**p["section"]) if p["section"] else None
                self.__subsection = (
                    Subsection(**p["subsection"]) if p["subsection"] else None
                )

    @property
    def title(self):
        if self.__title is None:
            self.__scrape_()
        return self.__title

    @property
    def language(self):
        if self.__language is None:
            self.__scrape_()
        return self.__language

    @property
    def summary(self):
        if self.__summary is None:
            self.__scrape_()
        return self.__summary

    @property
    def transcript(self):
        if self.__transcript is None:
            self.__scrape_()
        return self.__transcript

    @property
    def published(self):
        if self.__published is None:
            self.__scrape_()
        return self.__published

    @property
    def fileUrl(self):
        if self.__fileUrl is None:
            self.__scrape_()
        return self.__fileUrl

    @property
    def section(self):
        if self.__section is None:
            self.__scrape_()
        return self.__section

    @property
    def subsection(self):
        if self.__subsection is None:
            self.__scrape_()
        return self.__subsection

    def __repr__(self):
        return f"Audio(type, url, title, language, summary, transcript, published, fileUrl, section, subsection)"


class Video:
    def __init__(
        self,
        url,
        title=None,
        summary=None,
        authors=None,
        language=None,
        section=None,
        subsection=None,
        published=None,
        modified=None,
        duration=None,
        transcript=None,
        renditions=None,
        keyword=None,
        tags=None,
    ):
        self.type = "video"
        self.url = url
        self.__title = title
        self.__summary = summary
        self.__authors = Persons(authors) if authors else None
        self.__language = language
        self.__section = Section(**section) if section else None
        self.__subsection = Subsection(**subsection) if subsection else None
        self.__published = published
        self.__modified = modified
        self.__duration = duration
        self.__transcript = transcript
        self.__renditions = Renditions(renditions) if renditions else None
        self.__keyword = keyword
        self.__tags = tags
        self.__scrape = False
        self.__best_file = None

    def __getattr__(self, name):
        return None

    def download(self, path):
        self.renditions.download(path)

    def __scrape_(self):
        if self.__scrape is False:
            p = Scraper()._Scraper__get_video(self.url)
            self.__scrape = True

            if p:
                self.__title = p["title"]
                self.__summary = p["summary"]
                self.__authors = Persons(p["authors"]) if p["authors"] else None
                self.__language = p["language"]
                self.__section = Section(**p["section"]) if p["section"] else None
                self.__subsection = (
                    Subsection(**p["subsection"]) if p["subsection"] else None
                )
                self.__published = p["published"]
                self.__modified = p["modified"]
                self.__duration = p["duration"]
                self.__transcript = p["transcript"]
                self.__renditions = Renditions(p["renditions"])
                self.__keyword = p["keyword"]
                self.__tags = p["tags"]

    @property
    def title(self):
        if self.__title is None:
            self.__scrape_()
        return self.__title

    @property
    def summary(self):
        if self.__summary is None:
            self.__scrape_()
        return self.__summary

    @property
    def authors(self):
        if self.__authors is None:
            self.__scrape_()
        return self.__authors

    @property
    def language(self):
        if self.__language is None:
            self.__scrape_()
        return self.__language

    @property
    def section(self):
        if self.__section is None:
            self.__scrape_()
        return self.__section

    @property
    def subsection(self):
        if self.__subsection is None:
            self.__scrape_()
        return self.__subsection

    @property
    def published(self):
        if self.__published is None:
            self.__scrape_()
        return self.__published

    @property
    def modified(self):
        if self.__modified is None:
            self.__scrape_()
        return self.__modified

    @property
    def duration(self):
        if self.__duration is None:
            self.__scrape_()
        return self.__duration

    @property
    def transcript(self):
        if self.__transcript is None:
            self.__scrape_()
        return self.__transcript

    @property
    def renditions(self):
        if self.__renditions is None:
            self.__scrape_()
        return self.__renditions

    @property
    def keyword(self):
        if self.__keyword is None:
            self.__scrape_()
        return self.__keyword

    @property
    def tags(self):
        if self.__tags is None:
            self.__scrape_()
        return self.__tags

    def __repr__(self):
        return f"Video(type, url, title, summary, authors, language, section, subsection, published, modified, duration, transcript, renditions, keyword, tags)"


class Paidpost:
    def __init__(
        self,
        url,
        title,
        summary=None,
        language=None,
        published=None,
        modified=None,
        section=None,
        subsection=None,
        keyword=None,
        tags=None,
        advertiser=None,
        advertiserUrl=None,
        advertiserLogo=None,
        authors=None,
    ):
        self.type = "paidpost"
        self.url = url
        self.title = title
        self.__summary = summary
        self.__language = language
        self.__published = published
        self.__modified = modified
        self.__section = Section(**section) if section else None
        self.__subsection = Subsection(**subsection) if subsection else None
        self.__keyword = keyword
        self.__tags = tags
        self.__advertiser = advertiser
        self.__advertiserUrl = advertiserUrl
        self.__advertiserLogo = advertiserLogo
        self.__scrape = False

    def __getattr__(self, name):
        return None

    def __scrape_(self):
        if self.__scrape is False:
            p = Scraper()._Scraper__get_paidpost(self.url)
            self.__scrape = True

            if p:
                self.__summary = p["summary"]
                self.__language = p["language"]
                self.__published = p["published"]
                self.__modified = p["modified"]
                self.__section = Section(**p["section"]) if p["section"] else None
                self.__subsection = (
                    Subsection(**p["subsection"]) if p["subsection"] else None
                )
                self.__keyword = p["keyword"]
                self.__tags = p["tags"]
                self.__advertiser = p["advertiser"]
                self.__advertiserUrl = p["advertiserUrl"]
                self.__advertiserLogo = p["advertiserLogo"]

    @property
    def summary(self):
        if self.__summary is None:
            self.__scrape_()
        return self.__summary

    @property
    def language(self):
        if self.__language is None:
            self.__scrape_()
        return self.__language

    @property
    def published(self):
        if self.__published is None:
            self.__scrape_()
        return self.__published

    @property
    def modified(self):
        if self.__modified is None:
            self.__scrape_()
        return self.__modified

    @property
    def section(self):
        if self.__section is None:
            self.__scrape_()
        return self.__section

    @property
    def subsection(self):
        if self.__subsection is None:
            self.__scrape_()
        return self.__subsection

    @property
    def keyword(self):
        if self.__keyword is None:
            self.__scrape_()
        return self.__keyword

    @property
    def tags(self):
        if self.__tags is None:
            self.__scrape_()
        return self.__tags

    @property
    def advertiser(self):
        if self.__advertiser is None:
            self.__scrape_()
        return self.__advertiser

    @property
    def advertiserUrl(self):
        if self.__advertiserUrl is None:
            self.__scrape_()
        return self.__advertiserUrl

    @property
    def advertiserLogo(self):
        if self.__advertiserLogo is None:
            self.__scrape_()
        return self.__advertiserLogo

    def __repr__(self):
        return "Paidpost(type, url, title, summary, language, published, modified, section, subsection, keyword, tags, advertiser, advertiserUrl, advertiserLogo)"


class Slideshow:
    def __init__(
        self,
        url=None,
        title=None,
        summary=None,
        authors=None,
        language=None,
        section=None,
        subsection=None,
        slides=None,
        published=None,
        modified=None,
    ):
        self.type = "slideshow"
        self.url = url
        self.__title = title
        self.__summary = summary
        self.__authors = Persons(authors) if authors else None
        self.__language = language
        self.__section = Section(**section) if section else None
        self.__subsection = Subsection(**subsection) if subsection else None
        self.__published = published
        self.__modified = modified
        self.__slides = slides
        self.__scrape = False

    def __getattr__(self, name):
        return None

    def __scrape_(self):
        if self.__scrape is False:
            p = Scraper()._Scraper__get_slideshow(self.url)
            self.__scrape = True

            if p:
                self.__title = p["title"]
                self.__summary = p["summary"]
                self.__authors = Persons(p["authors"]) if p["authors"] else None
                self.__language = p["language"]
                self.__section = Section(**p["section"]) if p["section"] else None
                self.__subsection = (
                    Subsection(**p["subsection"]) if p["subsection"] else None
                )
                self.__published = p["published"]
                self.__modified = p["modified"]
                self.__slides = p["slides"]

    @property
    def title(self):
        if self.__title is None:
            self.__scrape_()
        return self.__title

    @property
    def summary(self):
        if self.__summary is None:
            self.__scrape_()
        return self.__summary

    @property
    def authors(self):
        if self.__authors is None:
            self.__scrape_()
        return self.__authors

    @property
    def language(self):
        if self.__language is None:
            self.__scrape_()
        return self.__language

    @property
    def section(self):
        if self.__section is None:
            self.__scrape_()
        return self.__section

    @property
    def subsection(self):
        if self.__subsection is None:
            self.__scrape_()
        return self.__subsection

    @property
    def published(self):
        if self.__published is None:
            self.__scrape_()
        return self.__published

    @property
    def modified(self):
        if self.__modified is None:
            self.__scrape_()
        return self.__modified

    @property
    def slides(self):
        if self.__slides is None:
            self.__scrape_()
        return self.__slides

    def __str__(self):
        return f"Slideshow(type, url, title, summary, authors, language, section, subsection, published, modified, slides)"


class Recipe:
    def __init__(
        self,
        url,
        title,
        summary,
        authors,
        adapted=None,
        image=None,
        time=None,
        rating=None,
        ratingCount=None,
        relatedArticles=None,
        relatedGuides=None,
        nutritionalInformation=None,
        yield_=None,
        ingredients=None,
        steps=None,
        tips=None,
        tags=None,
        published=None,
        modified=None,
    ):
        self.type = "recipe"
        self.url = url
        self.title = title
        self.summary = summary
        self.authors = Persons(authors)
        self.__adapted = adapted
        self.__image = image
        self.__time = time
        self.__rating = rating
        self.__ratingCount = ratingCount
        self.__relatedArticles = relatedArticles
        self.__relatedGuides = relatedGuides
        self.__nutritionalInformation = nutritionalInformation
        self.__yield_ = yield_
        self.__ingredients = ingredients
        self.__steps = steps
        self.__tips = tips
        self.__tags = tags
        self.__published = published
        self.__modified = modified
        self.__comments = None
        self.__scrape = False

    def __getattr__(self, name):
        return None

    def __scrape_(self):
        if self.__scrape is False:
            p = Scraper()._Scraper__get_recipe(self.url)
            self.__scrape = True

            if p:
                self.__adapted = p["adapted"]
                self.__image = p["image"]
                self.__time = p["time"]
                self.__rating = p["rating"]
                self.__ratingCount = p["ratingCount"]
                self.__relatedArticles = p["relatedArticles"]
                self.__relatedGuides = p["relatedGuides"]
                self.__nutritionalInformation = p["nutritionalInformation"]
                self.__yield_ = p["yield_"]
                self.__ingredients = p["ingredients"]
                self.__steps = p["steps"]
                self.__tips = p["tips"]
                self.__tags = p["tags"]
                self.__published = p.get("published")
                self.__modified = p.get("modified")

    @property
    def comments(self):
        if self.__comments is None:
            self.__comments = Scraper()._Scraper__get_comments(self.url)
        return self.__comments

    @property
    def adapted(self):
        if self.__adapted is None:
            self.__scrape_()
        return self.__adapted

    @property
    def image(self):
        if self.__image is None:
            self.__scrape_()
        return self.__image

    @property
    def time(self):
        if self.__time is None:
            self.__scrape_()
        return self.__time

    @property
    def rating(self):
        if self.__rating is None:
            self.__scrape_()
        return self.__rating

    @property
    def ratingCount(self):
        if self.__ratingCount is None:
            self.__scrape_()
        return self.__ratingCount

    @property
    def relatedArticles(self):
        if self.__relatedArticles is None:
            self.__scrape_()
        return self.__relatedArticles

    @property
    def relatedGuides(self):
        if self.__relatedGuides is None:
            self.__scrape_()
        return self.__relatedGuides

    @property
    def nutritionalInformation(self):
        if self.__nutritionalInformation is None:
            self.__scrape_()
        return self.__nutritionalInformation

    @property
    def yield_(self):
        if self.__yield_ is None:
            self.__scrape_()
        return self.__yield_

    @property
    def ingredients(self):
        if self.__ingredients is None:
            self.__scrape_()
        return self.__ingredients

    @property
    def steps(self):
        if self.__steps is None:
            self.__scrape_()
        return self.__steps

    @property
    def tips(self):
        if self.__tips is None:
            self.__scrape_()
        return self.__tips

    @property
    def tags(self):
        if self.__tags is None:
            self.__scrape_()
        return self.__tags

    @property
    def published(self):
        if self.__published is None:
            self.__scrape_()
        return self.__published

    @property
    def modified(self):
        if self.__modified is None:
            self.__scrape_()
        return self.__modified

    def __repr__(self):
        return f"Recipe(type, url, title, summary, comments, authors, adapted, image, time, rating, ratingCount, relatedArticles, relatedGuides, nutritionalInformation, yield, ingredients, steps, tips, tags, published, modified)"


class Article:
    def __init__(
        self,
        url,
        title,
        summary=None,
        authors=None,
        language=None,
        published=None,
        modified=None,
        section=None,
        subsection=None,
        alteration=None,
    ):
        self.type = "article"
        self.url = url
        self.title = title
        self.__summary = summary
        self.__authors = Persons(authors)
        self.__language = language
        self.__published = published
        self.__modified = modified
        self.__section = Section(**section) if section else None
        self.__subsection = Subsection(**subsection) if subsection else None
        self.__alteration = alteration
        self.__scrape = False

    def __getattr__(self, name):
        return None

    def __scrape_(self):
        if self.__scrape is False:
            p = Scraper()._Scraper__get_article(self.url)
            self.__scrape = True

            if p:
                self.__summary = p["summary"]
                self.__authors = Persons(p["authors"]) if p["authors"] else None
                self.__language = p["language"]
                self.__published = p["published"]
                self.__modified = p["modified"]
                self.__section = Section(**p["section"]) if p["section"] else None
                self.__subsection = (
                    Subsection(**p["subsection"]) if p["subsection"] else None
                )
                self.__alteration = p["alteration"]

    @property
    def language(self):
        if self.__language is None:
            self.__scrape_()
        return self.__language

    @property
    def summary(self):
        if self.__summary is None:
            self.__scrape_()
        return self.__summary

    @property
    def authors(self):
        if self.__authors is None:
            self.__scrape_()
        return self.__authors

    @property
    def published(self):
        if self.__published is None:
            self.__scrape_()
        return self.__published

    @property
    def modified(self):
        if self.__modified is None:
            self.__scrape_()
        return self.__modified

    @property
    def section(self):
        if self.__section is None:
            self.__scrape_()
        return self.__section

    @property
    def subsection(self):
        if self.__subsection is None:
            self.__scrape_()
        return self.__subsection

    @property
    def alteration(self):
        if self.__alteration is None:
            self.__scrape_()
        return self.__alteration

    def __repr__(self):
        return f"Article(type, url, title, summary, authors, language, published, modified, section, subsection, alteration)"


class Image:
    def __init__(self, url, name, typename, width, height):
        self.url = url
        self.name = name
        self.typename = typename
        self.__width = width
        self.__height = height
        self.__scrape = False

    def __scrape_(self):
        if self.__scrape is False:
            self.__scrape = True
            self.__width, self.__height = download.get_image_dimensions(self.url)

    def download(self, path):
        download.image(self.url, path)
        return True

    @property
    def width(self):
        if self.__width is None:
            self.__scrape_()
        return self.__width

    @property
    def height(self):
        if self.__height is None:
            self.__scrape_()
        return self.__height

    @property
    def size(self):
        return (self.width, self.height)

    def __repr__(self):
        return f"Image(url, name, typename, width, height, size)"


class Images(_Array):
    def __init__(self, images=None):
        if images is None:
            images = []

        super().__init__(clase=Image, elements=images)
        self.images = self.list

    def find(self, name=None, typename=None):
        for image in self.images:
            if (name is None or image.name == name) and (
                typename is None or image.typename == typename
            ):
                return image
        return None

    def download(self, path):
        image = self.find(name="superJumbo", typename="ImageRendition")
        if image:
            image.download(path)
            return True

    def __repr__(self):
        return f"Images({len(self.images)} image)"


class Entries(_Array):
    def __init__(self, entries=None):
        if entries is None:
            entries = []

        super().__init__(clase=None, elements=None)
        self.entries = self.list
        [self._Array__append(clase=_typename(x["url"]), element=x) for x in entries]

    def __repr__(self):
        return f"Entries({len(self.entries)} entries)"


class Person:
    def __init__(
        self,
        name,
        url=None,
        biography=None,
        photos=None,
        entries=None,
        social=None,
        totalEntries=None,
        pageInfo=None,
    ):
        self.type = "person"
        self.name = name.title()
        self.__url = url
        self.__biography = biography
        self.__photos = Images(photos) if photos else None
        self.__entries = Entries(entries) if entries else None
        self.__social = social
        self.__scrape = False
        self.__totalEntries = totalEntries
        self.__pageInfo = pageInfo

    def __cursor_next_page(self):
        if self.__pageInfo["hasNextPage"]:
            return self.__pageInfo["endCursor"]

    def __cursor_previus_page(self):
        if self.__pageInfo["hasPreviousPage"]:
            return self.__pageInfo["startCursor"]

    def next(self):
        cursor = self.__cursor_next_page()

        if cursor:
            response = Scraper()._Scraper__search_person(self.url, cursor)
            self.__pageInfo = response["pageInfo"]
            [
                self.entries._Array__append(clase=_typename(x["url"]), element=x)
                for x in response["entries"]
            ]
            return self.entries[-len(response["entries"]) :]

    def __scrape_(self):
        if self.__scrape is False:
            if self.__url is None:
                self.__url = self.url

            p = Scraper()._Scraper__get_person(self.url)
            self.__scrape = True

            if p:
                self.__biography = p["biography"]
                self.__photos = Images(p["photos"]) if p["photos"] else None
                self.__entries = Entries(p["entries"]) if p["entries"] else None
                self.__social = p["social"]
                self.__totalEntries = p["totalEntries"]
                self.__pageInfo = p["pageInfo"]

    @property
    def url(self):
        return "https://www.nytimes.com/by/{}".format(
            self.name.lower().replace(" ", "-")
        )

    @property
    def biography(self):
        if self.__biography is None:
            self.__scrape_()
        return self.__biography

    @property
    def photos(self):
        if self.__photos is None:
            self.__scrape_()
        return self.__photos

    @property
    def entries(self):
        if self.__entries is None:
            self.__scrape_()
        return self.__entries

    @property
    def social(self):
        if self.__social is None:
            self.__scrape_()
        return self.__social

    @property
    def totalEntries(self):
        if self.__totalEntries is None:
            self.__scrape_()
        return self.__totalEntries

    def __repr__(self):
        return (
            f"Person(type, url, name, biography, photos, entries, social, totalEntries)"
        )


class Persons(_Array):
    def __init__(self, persons=None):
        if persons is None:
            persons = []
        super().__init__(clase=Person, elements=persons)
        self.persons = self.list

    def find(self, name=None, url=None):
        for person in self.persons:
            if (name is None or person.name == name) and (
                url is None or person.url == url
            ):
                return person
        return None

    def __repr__(self):
        return f"Persons({len(self.persons)} person)"


class Default:
    def __init__(self, url, title, summary, authors, published, modified):
        self.type = "default"
        self.url = url
        self.title = title
        self.summary = summary
        self.authors = Persons(authors)
        self.published = published
        self.modified = modified

    def __getattr__(self, name):
        return None

    def __repr__(self):
        return "Default(type, url, title, summary, authors, published, modified)"


class Wirecutter(Default):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.type = "wirecutter"

    def __getattr__(self, name):
        return None

    def __repr__(self):
        return "Wirecutter(type, url, title, summary, authors, published, modified)"


class Newsgraphics(Default):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.type = "newsgraphics"

    def __getattr__(self, name):
        return None

    def __repr__(self):
        return "Newsgraphics(type, url, title, summary, authors, published, modified)"


def _typename(url):
    if "/video/" in url:
        return Video
    elif "/audio/" in url:
        return Audio
    elif "/slideshow/" in url:
        return Slideshow
    elif "/recipes/" in url:
        return Recipe
    elif "/interactive/" in url:
        return Interactive
    elif "/by/" in url:
        return Person
    elif "/paidpost/" in url:
        return Paidpost
    elif detect_article(url):
        return Article
    elif "/newsgraphics/" in url:
        return Newsgraphics
    elif "/wirecutter/" in url:
        return Wirecutter
    else:
        return Default
