from typing import List

import requests

endpoints = {
    'list': 'user/podcast/list',
    'new_releases': 'user/new_releases',
    'in_progress': 'user/in_progress',
    'starred': 'user/starred',
    'history': 'user/history',
    'stats': 'user/stats/summary',
    'search': 'discover/search',
    'recommendations': 'discover/recommend_episodes',
    'categories': 'categories_v2',
    'content': 'content',
    'featured': 'featured',
    'networks': 'network_list_v2',
    'popular': 'popular',
    'trending': 'trending'
}


def _get_endpoint(name: str) -> str:
    return endpoints.get(name)


def _make_url(base: str, endpoint: str, suffix: str = "") -> str:
    if endpoint.startswith("/"):
        endpoint = endpoint[1:]
    return f"{base}/{endpoint}{suffix}"


class Episode:
    def __init__(self, data: dict, podcast, api):
        self._data = data
        self.podcast = podcast
        self._api = api
        self.uuid = data.get('uuid')
        self.url = data.get('url')
        self.published_date = data.get('url')
        self.duration = data.get('duration')
        self.file_type = data.get('fileType')
        self.title = data.get('title')
        self.size = data.get('size')
        self.playing_status = data.get('playing_status')
        self.current_position = data.get('playedUpTo')
        self.starred = data.get('starred')
        self.podcast_uuid = data.get('podcastUuid')
        self.podcast_title = data.get('podcastTitle')
        self.episode_type = data.get('episodeType')
        self.season = data.get('episodeSeason')
        self.number = data.get('episodeNumber')
        self.deleted = data.get('isDeleted')


class Podcast:
    def __init__(self, data: dict, api):
        self._data = data
        self._api = api
        self.title = data.get('title')
        self.author = data.get('author')
        self.description = data.get('description')
        self.feed = data.get('feed')
        self.uuid = data.get('uuid')
        self.itunes = data.get('itunes')
        self.website = data.get('website')


class Category:
    def __init__(self, data: dict, api):
        self._data = data
        self._api = api
        self.name = data.get('name')
        self.icon = data.get('icon')
        self.source = data.get('source')

    def get_podcasts(self, region: str = 'us') -> List[Podcast]:
        url = self.source.replace('[regionCode]', region)
        data = self._api._get_json(url=url)
        return self._api._make_podcasts(json_data=data)


class PocketCast:
    def __init__(self, email: str, password: str):
        self._api_base = "https://api.pocketcasts.com"
        self._lists_base = "https://lists.pocketcasts.com"
        self._email = email
        self._password = password
        self._token = None
        self._session = requests.Session()
        self._login()

    def _login(self):
        url = _make_url(base=self._api_base, endpoint="user/login")
        json = {'email': self._email, 'password': self._password, 'scope': 'webplayer'}
        data = self._post_json(url=url, json=json)
        if data:
            self._token = data['token']

    def _get_json(self, url: str, params: dict = None) -> dict:
        res = self._session.get(url=url, params=params)
        if res:
            return res.json()
        return {}

    def _post_json(self, url: str, params: dict = None, data: dict = None, json: dict = None) -> dict:
        header = {'Authorization': f'Bearer {self._token}'} if self._token else None
        res = self._session.post(url=url, params=params, data=data, json=json, headers=header)
        if res:
            return res.json()
        return {}

    def _make_podcasts(self, json_data: dict) -> List[Podcast]:
        podcasts = []
        if json_data and json_data.get('podcasts'):
            for pod in json_data['podcasts']:
                podcasts.append(Podcast(data=pod, api=self))
        return podcasts

    def _make_episodes(self, json_data: dict) -> List[Episode]:
        episodes = []
        if json_data and json_data.get('episodes'):
            for ep in json_data['episodes']:
                episodes.append(Episode(data=ep, podcast=None, api=self))
        return episodes

    def _make_categories(self, json_data: dict) -> List[Category]:
        categories = []
        if json_data:
            for cat in json_data:
                categories.append(Category(data=cat, api=self))
        return categories

    @property
    def stats(self) -> dict:
        endpoint = _get_endpoint("stats")
        url = _make_url(base=self._api_base, endpoint=endpoint)
        return self._post_json(url=url)

    @property
    def subscriptions(self) -> List[Podcast]:
        endpoint = _get_endpoint("list")
        url = _make_url(base=self._api_base, endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def in_progress(self) -> List[Episode]:
        endpoint = _get_endpoint("in_progress")
        url = _make_url(base=self._api_base, endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def starred(self) -> List[Episode]:
        endpoint = _get_endpoint("starred")
        url = _make_url(base=self._api_base, endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def history(self) -> List[Episode]:
        endpoint = _get_endpoint("history")
        url = _make_url(base=self._api_base, endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def new_releases(self) -> List[Episode]:
        endpoint = _get_endpoint("new_releases")
        url = _make_url(base=self._api_base, endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def recommendations(self) -> List[Episode]:
        endpoint = _get_endpoint("recommendations")
        url = _make_url(base=self._api_base, endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    def search(self, keyword: str) -> List[Podcast]:
        endpoint = _get_endpoint("search")
        url = _make_url(base=self._api_base, endpoint=endpoint)
        data = self._post_json(url=url, data={"term": keyword})
        return self._make_podcasts(json_data=data)

    @property
    def categories(self) -> List[Category]:
        data = self._get_json(url="https://static.pocketcasts.com/discover/json/categories_v2.json")
        return self._make_categories(json_data=data)

    @property
    def trending(self) -> List[Podcast]:
        endpoint = _get_endpoint("trending")
        url = _make_url(base=self._lists_base, endpoint=endpoint, suffix=".json")
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def popular(self) -> List[Podcast]:
        endpoint = _get_endpoint("popular")
        url = _make_url(base=self._lists_base, endpoint=endpoint, suffix=".json")
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def featured(self) -> List[Podcast]:
        endpoint = _get_endpoint("featured")
        url = _make_url(base=self._lists_base, endpoint=endpoint, suffix=".json")
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def networks(self):
        return []

    @property
    def content(self):
        return []
