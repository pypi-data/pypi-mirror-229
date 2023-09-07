import requests
from nyt_scraper.src import helpers
from nyt_scraper.src.Scraper.parser import general
from nyt_scraper.src.Scraper.parser import typename as typename__
import time


class Scraper:
    def __init__(self):
        self.headers = {
            "authority": "samizdat-graphql.nytimes.com",
            "accept": "*/*",
            "accept-language": "es-ES,es;q=0.9",
            "content-type": "application/json",
            "nyt-app-type": "project-vi",
            "nyt-app-version": "0.0.5",
            "nyt-token": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs+/oUCTBmD/cLdmcecrnBMHiU/pxQCn2DDyaPKUOXxi4p0uUSZQzsuq1pJ1m5z1i0YGPd1U1OeGHAChWtqoxC7bFMCXcwnE1oyui9G1uobgpm1GdhtwkR7ta7akVTcsF8zxiXx7DNXIPd2nIJFH83rmkZueKrC4JVaNzjvD+Z03piLn5bHWU6+w+rA+kyJtGgZNTXKyPh6EC6o5N+rknNMG5+CdTq35p8f99WjFawSvYgP9V64kgckbTbtdJ6YhVP58TnuYgr12urtwnIqWP9KSJ1e5vmgf3tunMqWNm6+AnsqNj8mCLdCuc5cEB74CwUeQcP2HQQmbCddBy2y0mEwIDAQAB",
            "origin": "https://www.nytimes.com",
            "referer": "https://www.nytimes.com/",
            "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "x-nyt-internal-meter-override": "undefined",
        }

    def __check_error(self, response):
        Json = response.json()

        if Json.get("errors"):
            if Json["errors"][0]["message"] == "PersistedQueryNotFound":
                return True
        return False

    def __search(self, keyword, sort="best", type_="", section="", cursor=None):
        # sort: "newest", "oldest" y "best"

        originalType, originalSection = type_, section

        sort = helpers.format_sort(sort)

        if type_:
            type_ = helpers.format_data_types(type_.lower(), key="type")

        if section:
            section = helpers.format_data_section(section)

        filterQuery = helpers.make_filterQuery(type_, section)
        json_data = {
            "operationName": "SearchRootQuery",
            "variables": {
                "first": 10,
                "sort": sort,
                "text": keyword,
                "filterQuery": filterQuery,
                "sectionFacetFilterQuery": type_,
                "typeFacetFilterQuery": section,
                "sectionFacetActive": False,
                "typeFacetActive": False,
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "57637487214907d9fded37e092695fcc12dcf8d819b36ae657056d8f42151c89",
                },
            },
        }
        if cursor:
            json_data["variables"]["cursor"] = cursor

        response = requests.post(
            "https://samizdat-graphql.nytimes.com/graphql/v2",
            headers=self.headers,
            json=json_data,
        )

        if response.status_code == 200:
            if self.__check_error(response):
                time.sleep(2)
                return self.__search(keyword, sort, type_, section, cursor)

            query = {
                "keyword": keyword,
                "sort": sort,
                "type_": originalType,
                "section": originalSection,
                "cursor": cursor,
            }
            r = general.parser_search(response)
            r["query"] = query
            return r

    def __search_person(self, url, cursor=None):
        headers = {
            "authority": "samizdat-graphql.nytimes.com",
            "accept": "*/*",
            "accept-language": "es-ES,es;q=0.8",
            "content-type": "application/json",
            "nyt-app-type": "project-vi",
            "nyt-app-version": "0.0.5",
            "nyt-token": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs+/oUCTBmD/cLdmcecrnBMHiU/pxQCn2DDyaPKUOXxi4p0uUSZQzsuq1pJ1m5z1i0YGPd1U1OeGHAChWtqoxC7bFMCXcwnE1oyui9G1uobgpm1GdhtwkR7ta7akVTcsF8zxiXx7DNXIPd2nIJFH83rmkZueKrC4JVaNzjvD+Z03piLn5bHWU6+w+rA+kyJtGgZNTXKyPh6EC6o5N+rknNMG5+CdTq35p8f99WjFawSvYgP9V64kgckbTbtdJ6YhVP58TnuYgr12urtwnIqWP9KSJ1e5vmgf3tunMqWNm6+AnsqNj8mCLdCuc5cEB74CwUeQcP2HQQmbCddBy2y0mEwIDAQAB",
            "origin": "https://www.nytimes.com",
            "referer": "https://www.nytimes.com/",
            "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "x-nyt-internal-meter-override": "undefined",
        }

        json_data = {
            "operationName": "BylineQuery",
            "variables": {
                "id": "/by/" + url.split("/by/")[1],
                "first": 10,
                "streamQuery": {
                    "sort": "newest",
                },
                "exclusionMode": "HIGHLIGHTS_AND_EMBEDDED",
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "81946cc09e695f69de07ae9ea9464a0482184d22be099c11e616f28f9e3ca377",
                },
            },
        }

        if cursor:
            json_data["variables"]["cursor"] = cursor

        response = requests.post(
            "https://samizdat-graphql.nytimes.com/graphql/v2",
            headers=headers,
            json=json_data,
        )

        if response.status_code == 200:
            r = general.parser_person(response)
            return r

    def __search_suggest(self, query):
        json_data = {
            "operationName": "SearchSuggestQuery",
            "variables": {
                "text": query,
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "60f2741ce865787e148a10228976f9c6a5178f187a451c41fd34b6280ff5e843",
                },
            },
        }

        response = requests.post(
            "https://samizdat-graphql.nytimes.com/graphql/v2",
            headers=self.headers,
            json=json_data,
        )

        if response.status_code == 200:
            Data = response.json()["data"]["searchSuggest"]
            del Data["__typename"]
            return Data

    def __get_comments(self, link, max_comments=999999):
        headers = {
            "authority": "www.nytimes.com",
            "accept": "*/*",
            "accept-language": "es-ES,es;q=0.6",
            "content-type": "application/json",
            "origin": "https://cooking.nytimes.com",
            "referer": "https://cooking.nytimes.com/",
            "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }
        params = {
            "cmd": "GetCommentsAll",
            "sort": "newest",
            "limit": str(max_comments),
            "offset": "0",
            "url": link,
        }

        response = requests.get(
            "https://www.nytimes.com/svc/community/V3/requestHandler",
            params=params,
            headers=headers,
        )
        if response.status_code == 200:
            return general.parser_comments(response)

    def __get(self, url, typename):
        typename__.check(url, typename)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

        response = requests.get(
            url,
            headers=headers,
        )

        if response.status_code == 200 and "archive.nytimes.com" not in response.url:
            func, _ = typename__.get(url)
            return general.get(func, response)
        return None

    def __get_audio(self, url):
        return self.__get(url, "audio")

    def __get_video(self, url):
        return self.__get(url, "video")

    def __get_slideshow(self, url):
        return self.__get(url, "slideshow")

    def __get_article(self, url):
        return self.__get(url, "article")

    def __get_recipe(self, url):
        return self.__get(url, "recipe")

    def __get_interactive(self, url):
        return self.__get(url, "interactive")

    def __get_paidpost(self, url):
        return self.__get(url, "paidpost")

    def __get_person(self, url):
        return self.__search_person(url)
