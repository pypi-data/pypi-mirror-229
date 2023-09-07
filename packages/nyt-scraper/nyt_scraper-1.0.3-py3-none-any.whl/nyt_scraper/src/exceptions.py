class NewsGraphicsScrapingNotAllowed(Exception):
    def __init__(self, message="You can't scrape newsgraphics pages."):
        self.message = message
        super().__init__(self.message)


class WirecutterScrapingNotAllowed(Exception):
    def __init__(self, message="You can't scrape wirecutter pages."):
        self.message = message
        super().__init__(self.message)


class PageNotAllowed(Exception):
    def __init__(self, message="You can't scrape this page."):
        self.message = message
        super().__init__(self.message)


class InvalidSection(Exception):
    def __init__(
        self, message="Section not is valid. You can use name or uri of section."
    ):
        self.message = message
        super().__init__(self.message)
