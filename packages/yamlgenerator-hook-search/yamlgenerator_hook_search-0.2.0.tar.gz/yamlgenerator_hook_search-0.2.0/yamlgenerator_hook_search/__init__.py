from re import sub
from urllib.parse import quote_plus

from loguru import logger
from gameyamlspiderandgenerator.util.config import config
from gameyamlspiderandgenerator.hook import BaseHook
from gameyamlspiderandgenerator.util.spider import get_json, get_text
from gameyamlspiderandgenerator.util.thread import ThreadWithReturnValue
from bs4 import BeautifulSoup


# print(config, type(config))

class Search(BaseHook):
    CHANGED = ["tags", "links", "publish", "platform"]

    def __init__(self):
        self.pure = None
        self.encode = None

    @staticmethod
    def name_filter(string: str, pattern: str = r"[^A-z]", repl: str = ""):
        """

        Args:
            string: The string to be replaced
            pattern: Regular expression, replace non-English letters by default
            repl: The string to replace with

        Returns:

        """
        return sub(pattern, repl, string)

    def search_play(self) -> tuple:
        """
        publish
        """
        data = get_json(
            "https://serpapi.com/search?engine=google_play&apikey="
            f'{config["api"]["google-play"]}&store=apps&q={self.encode}'
        )
        if "organic_results" in data and any(
                [self.name_filter(i["title"]) == self.pure for i in data["organic_results"][0]["items"]]):
            logger.info("FOUND: google_play")
            return "google-play", {'name': '.play-store',
                                   'uri':
                                       f'google-play-store:{data["organic_results"][0]["items"][0]["product_id"]}'}
        return None, None

    def search_apple(self) -> tuple:
        """
        publish
        """
        data = get_json(
            "https://serpapi.com/search.json?engine=apple_app_store&term="
            f'{self.encode}&apikey={config["api"]["apple"]}'
        )
        if "organic_results" in data and any(
                [self.name_filter(i["title"]) == self.pure for i in data["organic_results"]]):
            logger.info("FOUND: apple_app_store")
            return "apple-appstore", {'name': '.apple-appstore', 'uri': data["organic_results"][0]["link"]}
        return None, None

    def search_all(self, type_tag: str) -> list:
        """
        publish
        """
        func_list = [
            self.__getattribute__(i)
            for i in (list(filter(lambda x: "__" not in x, self.__dir__())))
        ]

        func_list = list(filter(
            lambda x: callable(x)
                      and x.__name__.startswith("search")
                      and x.__name__ != "search_all"
                      and x.__doc__.strip() == type_tag,
            func_list,
        ))
        fn_list = [ThreadWithReturnValue(target=i) for i in func_list]
        for i in fn_list:
            i.start()
        return [ii.join() for ii in fn_list]

    def search_epic(self):
        """
        publish
        """
        from epicstore_api import EpicGamesStoreAPI
        api = EpicGamesStoreAPI().fetch_store_games(keywords=self.encode, sort_dir="DESC")
        game_list = api['data']['Catalog']['searchStore']['elements']
        reg = r"[^A-z\d]"
        if game_list and any(
                [self.name_filter(i["title"]) == self.pure for i in game_list]):
            logger.info("FOUND: epic")
            return "epic", {'name': '.epic',
                            'uri': f'https://store.epicgames.com/p/'
                                   f'{self.name_filter(game_list[0]["title"], pattern=reg, repl="-")}'}
        return None, None

    def search_xbox(self):
        """
        platform
        """
        search_string = self.pure
        data = BeautifulSoup(get_text(f"https://www.xbox.com/en-us/search?q={quote_plus(search_string)}"
                                      ), features="lxml")

        if data.select_one('#nav-general > div > div') is None:
            return None, None
        else:
            data = data.select('#nav-general > div > div:nth-child(2) > div > h3 > a')
            data1 = [(i.attrs['href'], i.text.strip()) for i in data]
            for _, i in data1:
                if search_string.replace(" ","").lower() in i.replace(" ","").lower():
                    return "xbox-one", None
            return None,None

    def setup(self, data: dict):
        """
        hook handler
        Args:
            data: yaml data

        Returns:
            The processed dict data

        """
        self.pure = self.name_filter(data['name'])
        self.encode = quote_plus(self.name_filter(data['name'], repl=" "))
        temp = data.copy()
        result = self.search_all('publish')
        publish = set([i for i,ii in result if i is not None]) | set(temp["tags"]['publish']) - {None}
        link = [ii for i,ii in result if ii is not None]
        result = self.search_all('platform')
        platform = set([i for i,ii in result if i is not None]) | set(temp["tags"]["platform"]) - {None}
        link = link+[ii for i,ii in result if ii is not None]+temp["links"]
        temp["tags"]['publish'] = list(publish)
        temp["links"] = list(link)
        temp["tags"]["platform"] = list(platform)
        return temp

