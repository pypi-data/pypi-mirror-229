from typing import Dict, List, Tuple
from urllib.parse import urlsplit

from parsel import Selector
from scrape_schema import Parsel, Sc, sc_param

from anicli_api.base import BaseAnime, BaseEpisode, BaseExtractor, BaseOngoing, BaseSearch, BaseSource


class Extractor(BaseExtractor):
    BASE_URL = "https://animego.org"

    def search(self, query: str) -> List["Search"]:
        response = self.HTTP().get(f"{self.BASE_URL}/search/anime", params={"q": query})
        chunks = (
            Parsel()
            .xpath(
                "//div[@class='row']/div[@class='animes-grid-item col-6 col-sm-6 col-md-4 col-lg-3 col-xl-2 col-ul-2']"
            )
            .sc_parse(response.text)
        )
        return [Search(chunk) for chunk in chunks.getall()]

    async def a_search(self, query: str) -> List["Search"]:
        async with self.HTTP_ASYNC() as client:
            response = await client.get(f"{self.BASE_URL}search/anime", params={"q": query})
            chunks = (
                Parsel()
                .xpath(
                    "//div[@class='row']/div[@class='animes-grid-item col-6 col-sm-6 col-md-4 col-lg-3 col-xl-2 "
                    "col-ul-2']"
                )
                .getall()
                .sc_parse(response.text)
            )
            return [Search(chunk) for chunk in chunks]

    @staticmethod
    def _ongoing_clear_dupes(ongoings: List["Ongoing"]) -> List["Ongoing"]:
        """remove url duplicates for decrease output result"""
        result: Dict[Tuple[int, str], Ongoing] = {}
        for ongoing in ongoings:
            tuple_key = (ongoing.num, ongoing.url)
            if not result.get(tuple_key, None):
                result[tuple_key] = ongoing
            else:
                result[tuple_key].dub += f", {ongoing.dub}"
        return list(result.values())

    def ongoing(self) -> List["Ongoing"]:
        response = self.HTTP().get(self.BASE_URL)
        chunks = Parsel().xpath('//*[starts-with(@class, "last-update-item")]').getall().sc_parse(response.text)
        return self._ongoing_clear_dupes([Ongoing(chunk) for chunk in chunks])

    async def a_ongoing(self) -> List["Ongoing"]:
        async with self.HTTP_ASYNC() as client:
            response = await client.get(self.BASE_URL)
            chunks = Parsel().xpath('//*[starts-with(@class, "last-update-item")]').getall().sc_parse(response.text)
            return self._ongoing_clear_dupes([Ongoing(chunk) for chunk in chunks])


class Search(BaseSearch):
    title: Sc[
        str,
        Parsel().xpath("//div[@class='h5 font-weight-normal mb-2 card-title text-truncate']/a/@title").get(),
    ]
    url: Sc[
        str,
        Parsel().xpath("//div[@class='h5 font-weight-normal mb-2 card-title text-truncate']/a/@href").get(),
    ]
    thumbnail: Sc[str, Parsel().xpath("//a/div/@data-original").get()]

    rating: Sc[
        float,
        Parsel(default=0.0).xpath("//div[@class='p-rate-flag__text']/text()").get().sc_replace(",", "."),
    ]
    name: Sc[
        str,
        Parsel().xpath("//div[@class='text-gray-dark-6 small mb-1 d-none d-sm-block']/div/text()").get(),
    ]

    def __str__(self):
        return f"{self.title} [{self.name}] ({self.rating}/10)"

    def get_anime(self) -> "Anime":
        response = self.HTTP().get(self.url)
        return Anime(response.text)

    async def a_get_anime(self) -> "Anime":
        async with self.HTTP_ASYNC() as client:
            response = await client.get(self.url)
            return Anime(response.text)


class Ongoing(BaseOngoing):
    _onclick: Sc[str, Parsel().xpath("//div/@onclick").get()]
    _thumb_style: Sc[str, Parsel().xpath("//div[@class='img-square lazy br-50']/@style").get()]

    title: Sc[str, Parsel().xpath("//span[@class='last-update-title font-weight-600']/text()").get()]
    thumbnail: str = sc_param(lambda self: self._thumb_style.replace("background-image: url(", "").replace(");", ""))

    @sc_param
    def url(self) -> str:
        path = self._onclick.replace("location.href='", "").replace("'", "")
        return f"https://animego.org{path}"

    name: Sc[str, Parsel().xpath("//div[@class='font-weight-600 text-truncate']/text()").get()]
    dub: Sc[
        str,
        Parsel().xpath("//div[@class='ml-3 text-right']/div[@class='text-gray-dark-6']/text()").get(),
    ]

    def __str__(self):
        return f"{self.title} {self.name} ({self.dub})"

    @sc_param
    def num(self) -> int:
        return int(self.name.replace(" серия", "").replace(" Серия", ""))

    def get_anime(self) -> "Anime":
        response = self.HTTP().get(self.url)
        return Anime(response.text)

    async def a_get_anime(self) -> "Anime":
        async with self.HTTP_ASYNC() as client:
            response = await client.get(self.url)
            return Anime(response.text)


class Anime(BaseAnime):
    _script_jmespath: Sc[Selector, Parsel(auto_type=False).xpath("//script[@type='application/ld+json']/text()")]

    @sc_param
    def title(self) -> str:
        return self._script_jmespath.jmespath("name").get()

    @sc_param
    def alt_titles(self) -> List[str]:
        return self._script_jmespath.jmespath("alternativeHeadline").getall()

    episodes_available: Sc[int, Parsel(default=0).xpath("//dl/dd[2]/text()").re(r"\d+")[0]]
    thumbnail: Sc[str, Parsel().css("#content img").xpath("@src").get()]
    _description: Sc[List[str], Parsel().xpath("//div[@data-readmore='content']/text()").getall()]  # mobile agent

    @sc_param
    def description(self) -> str:
        return " ".join(s.strip() for s in self._description)

    @sc_param
    def genres(self) -> List[str]:
        return self._script_jmespath.jmespath("genre").getall()

    @sc_param
    def episodes_total(self) -> int:
        return int(self._script_jmespath.jmespath("numberOfEpisodes").get())

    @sc_param
    def aired(self) -> str:
        if end_date := self._script_jmespath.jmespath("endDate").get():
            return self._script_jmespath.jmespath("startDate").get() + " " + end_date
        return self._script_jmespath.jmespath("startDate").get() + " " + "?"

    url: Sc[str, Parsel().xpath("//html/head/link[@rel='canonical']/@href").get()]
    anime_id = sc_param(lambda self: self.url.split("-")[-1])

    @sc_param
    def rating(self) -> float:
        return float(self._script_jmespath.jmespath("aggregateRating.ratingValue").get())

    @staticmethod
    def _get_dubbers(response: str) -> Dict[str, str]:
        # sel = Selector(response)
        dubbers_id: List[str] = (
            Parsel().xpath('//*[@id="video-dubbing"]/span/@data-dubbing').getall().sc_parse(response)
        )
        dubbers_name: List[str] = (
            Parsel()
            .xpath('//*[@id="video-dubbing"]/span/span/text()')
            .getall()
            .fn(lambda lst: [s.strip() for s in lst])
            .sc_parse(response)
        )
        return dict(zip(dubbers_id, dubbers_name))

    def get_episodes(self) -> List["Episode"]:
        response = self.HTTP().get(f"https://animego.org/anime/{self.anime_id}/player?_allow=true").json()["content"]

        _dubbers_table = self._get_dubbers(response)
        chunks = Parsel().xpath('//*[@id="video-carousel"]/div/div').getall().sc_parse(response)
        episodes = [Episode(chunk) for chunk in chunks]
        for ep in episodes:
            setattr(ep, "_dubbers_table", _dubbers_table)
        return episodes

    async def a_get_episodes(self) -> List["Episode"]:
        async with self.HTTP_ASYNC() as client:
            response = await client.get(self.url)
            _dubbers_table = self._get_dubbers(response)
            chunks = Parsel().xpath('//*[@id="video-carousel"]/div/div').getall().sc_parse(response)
            episodes = [Episode(chunk) for chunk in chunks]
            for ep in episodes:
                setattr(ep, "_dubbers_table", _dubbers_table)
            return episodes


class Episode(BaseEpisode):
    _episode_type: Sc[int, Parsel().xpath("//div/@data-episode-type").get()]
    _dubbers_table: Dict[str, str]  # setattr
    num: Sc[int, Parsel().xpath("//div/@data-episode").get()]
    title: Sc[str, Parsel().xpath("//div/@data-episode-title").get()]

    data_id: Sc[int, Parsel().xpath("//div/@data-id").get()]
    released: Sc[str, Parsel().xpath("//div/@data-episode-released").get()]

    def __str__(self):
        return f"{self.title} {self.num} {self.released}"

    def get_sources(self) -> List["Source"]:
        response = (
            self.HTTP()
            .get(
                "https://animego.org/anime/series",
                params={"dubbing": 2, "provider": 24, "episode": self.num, "id": self.data_id},
            )
            .json()["content"]
        )

        chunks = Parsel().xpath('//*[@id="video-players"]/span').getall().sc_parse(response)
        sources = [Source(chunk) for chunk in chunks]
        for source in sources:
            setattr(source, "_dubbers_table", self._dubbers_table)
        return sources

    async def a_get_sources(self) -> List["Source"]:
        async with self.HTTP_ASYNC() as client:
            response = await client.get(
                "https://animego.org/anime/series",
                params={"dubbing": 2, "provider": 24, "episode": self.num, "id": self.data_id},
            ).json()["content"]
            chunks = Parsel().xpath('//*[@id="video-players"]/span').getall().sc_parse(response)
            sources = [Source(chunk) for chunk in chunks]
            for source in sources:
                setattr(source, "_dubbers_table", self._dubbers_table)
            return sources


class Source(BaseSource):
    _dubbers_table: Dict[str, str]
    _url: Sc[str, Parsel().xpath("//span/@data-player").get()]
    _data_provider: Sc[str, Parsel().xpath("//span/@data-provider").get()]
    _data_provide_dubbing: Sc[str, Parsel().xpath("//span/@data-provide-dubbing").get()]
    name: Sc[str, Parsel().xpath("//span/span/text()").get()]
    url = sc_param(lambda self: f"https:{self._url}")
    dub = sc_param(lambda self: self._dubbers_table.get(self._data_provide_dubbing))

    def __str__(self):
        return f"{urlsplit(self.url).netloc} {self.name} ({self.dub})"


if __name__ == "__main__":
    import logging

    logger = logging.getLogger("scrape_schema")
    logger.setLevel(logging.DEBUG)
    ex = Extractor()
    # res = ex.ongoing()
    res = ex.search("lain")
    an = res[0].get_anime()
    eps = an.get_episodes()
    sources = eps[0].get_sources()
    print()
    # ongs = ex.ongoing()
    # an2 = ongs[0].get_anime()
    # print()
    # episodes = an.get_episodes()
    # sss = episodes[0].get_sources()
    # vids = sss[0].get_videos()
    # print(*vids)
