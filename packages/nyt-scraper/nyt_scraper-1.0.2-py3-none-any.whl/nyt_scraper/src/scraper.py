from nyt_scraper.src.Scraper.scraper import Scraper as __Scraper
from nyt_scraper.src import entities


class Scraper(__Scraper):
    def search(self, keyword: str, sort="best", type_="", section=""):
        """
        Performs a search in the New York Times database.

        Args:
            keyword (str): Search term.
            sort (str, optional): Sorting order ("newest", "oldest", "best").
            type_ (str, optional): Content type to filter.
            section (str, optional): Section to filter.
        """
        r = self.__search(keyword, sort, type_, section)

        if r:
            return entities.Search(**r)

    def search_suggest(self, query: str):
        """
        Retrieves search suggestions for a given search term.

        Args:
            query (str): Search term.
        """
        return self.__search_suggest(query)

    def get_video(self, url: str):
        """
        Retrieves video content from a URL.

        Args:
            url (str): URL of the video content.
        """
        r = self.__get(url, "video")

        if r:
            return entities.Video(**r)

    def get_audio(self, url: str):
        """
        Retrieves audio content from a URL.

        Args:
            url (str): URL of the audio content.
        """
        r = self.__get(url, "audio")

        if r:
            return entities.Audio(**r)

    def get_slideshow(self, url: str):
        """
        Retrieves slideshow content from a URL.

        Args:
            url (str): URL of the slideshow content.
        """
        r = self.__get(url, "slideshow")

        if r:
            return entities.Slideshow(**r)

    def get_article(self, url: str):
        """
        Retrieves article content from a URL.

        Args:
            url (str): URL of the article content.
        """
        r = self.__get(url, "article")

        if r:
            return entities.Article(**r)

    def get_recipe(self, url: str):
        """
        Retrieves recipe content from a URL.

        Args:
            url (str): URL of the recipe content.
        """
        r = self.__get(url, "recipe")

        if r:
            return entities.Recipe(**r)

    def get_interactive(self, url: str):
        """
        Retrieves interactive content from a URL.

        Args:
            url (str): URL of the interactive content.
        """
        r = self.__get(url, "interactive")

        if r:
            return entities.Interactive(**r)

    def get_paidpost(self, url: str):
        """
        Retrieves paidpost content from a URL.

        Args:
            url (str): URL of the paidpost content.
        """
        r = self.__get(url, "paidpost")

        if r:
            return entities.Paidpost(**r)

    def get_person(self, url: str):
        """
        Performs a search for information about a person.

        Args:
            url (str): URL of the person.
        """
        r = self.__search_person(url)

        if r:
            return entities.Person(**r)
