from typing import List, Union

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
    'trending': 'trending',
    'episodes': 'user/podcast/episodes',
    'subscribe': 'user/podcast/subscribe',
    'unsubscribe': 'user/podcast/unsubscribe',
    'episode_archive': 'sync/update_episode_archive',
    'up_next': 'up_next/list',
    'play_status': 'sync/update_episode',
    'play_next': 'up_next/play_next',
    'play_last': 'up_next/play_last'
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

    @property
    def show_notes(self) -> str:
        url = f"https://podcast-api.pocketcasts.com/episode/show_notes/{self.uuid}"
        print(url)
        data = self._api._get_json(url=url, include_token=True)
        return data.get('show_notes', "")

    def mark_played(self) -> bool:
        endpoint = _get_endpoint("play_status")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.uuid,
                                 'podcast': self.podcast.uuid,
                                 'status': 3
                                 }
                           ):
            return True
        return False

    def mark_unplayed(self) -> bool:
        endpoint = _get_endpoint("play_status")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.uuid,
                                 'podcast': self.podcast.uuid,
                                 'status': 1,
                                 'position': 0
                                 }
                           ):
            return True
        return False

    def archive(self) -> bool:
        endpoint = _get_endpoint("episode_archive")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           data={'episodes': [
                               {'uuid': self.uuid,
                                'podcast': self.podcast.uuid
                                }
                           ],
                               'archive': True}):
            return True
        return False

    def unarchive(self) -> bool:
        endpoint = _get_endpoint("episode_archive")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'episodes': [
                               {'uuid': self.uuid,
                                'podcast': self.podcast.uuid
                                }
                           ],
                               'archive': False}):
            return True
        return False

    def play_next(self) -> bool:
        endpoint = _get_endpoint("play_next")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           data={'version': 2,
                                 'episode': {'uuid': self.uuid,
                                             'title': self.title,
                                             'url': self.url,
                                             'podcast': self.podcast.uuid,
                                             'published': self.published_date
                                             }
                                 }
                           ):
            return True
        return False

    def play_last(self) -> bool:
        endpoint = _get_endpoint("play_last")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           data={'version': 2,
                                 'episode': {'uuid': self.uuid,
                                             'title': self.title,
                                             'url': self.url,
                                             'podcast': self.podcast.uuid,
                                             'published': self.published_date
                                             }
                                 }
                           ):
            return True
        return False

    """
    @property
    def full_details(self):
        url = f"https://podcasts.pocketcasts.com/{self.podcast.uuid}/episodes_full_{self.uuid}.json"
        return self._api._get_json(url=url)
    """


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

    @property
    def episodes(self) -> List[Episode]:
        endpoint = _get_endpoint("episodes")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        data = self._api._post_json(url=url,
                                    data={'uuid': self.uuid})
        return self._api._make_episodes(json_data=data,
                                        podcast=self)

    def subscribe(self) -> bool:
        endpoint = _get_endpoint("subscribe")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.uuid}):
            return True
        return False

    def unsubscribe(self) -> bool:
        endpoint = _get_endpoint("unsubscribe")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.uuid}):
            return True
        return False


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


class Account:
    def __init__(self, data: dict, api):
        self._data = data
        self._api = api
        self.paid = True if data.get('paid') == 1 else False
        self.platform = data.get('platform')
        self.expiry_date = data.get('expiryDate')
        self.auto_renewing = data.get('autoRenewing')
        self.gift_days = data.get('giftDays')
        self.cancel_url = data.get('cancelUrl')
        self.update_url = data.get('updateUrl')
        self.frequency = data.get('frequency')
        self.web = data.get('web')


class PocketCast:
    def __init__(self, email: str, password: str):
        self._api_base = "https://api.pocketcasts.com"
        self._lists_base = "https://lists.pocketcasts.com"
        self._email = email
        self._password = password
        self._token = None
        self._login()

    def _login(self):
        url = _make_url(base=self._api_base,
                        endpoint="user/login")
        json = {'email': self._email,
                'password': self._password,
                'scope': 'webplayer'}
        data = self._post_json(url=url,
                               json=json)
        if data:
            self._token = data['token']

    def _get(self,
             url: str,
             params: dict = None,
             include_token: bool = False) -> requests.Response:
        return requests.get(url=url,
                            params=params,
                            headers=({'Authorization': f'Bearer {self._token}'}
                                     if include_token else None))

    def _post(self,
              url: str,
              params: dict = None,
              data: dict = None,
              json: dict = None) -> requests.Response:
        header = {'Authorization': f'Bearer {self._token}'} if self._token else None
        return requests.post(url=url,
                             params=params,
                             data=data,
                             json=json,
                             headers=header)

    def _get_json(self,
                  url: str,
                  params: dict = None,
                  include_token: bool = False) -> dict:
        res = self._get(url=url,
                        params=params,
                        include_token=include_token)
        if res:
            return res.json()
        return {}

    def _post_json(self,
                   url: str,
                   params: dict = None,
                   data: dict = None,
                   json: dict = None) -> dict:
        res = self._post(url=url,
                         params=params,
                         data=data,
                         json=json)
        if res:
            return res.json()
        return {}

    def _make_podcasts(self,
                       json_data: dict) -> List[Podcast]:
        podcasts = []
        if json_data and json_data.get('podcasts'):
            for pod in json_data['podcasts']:
                podcasts.append(Podcast(data=pod, api=self))
        return podcasts

    def _make_episodes(self,
                       json_data: dict,
                       podcast: Podcast = None) -> List[Episode]:
        episodes = []
        if json_data and json_data.get('episodes'):
            for ep in json_data['episodes']:
                episodes.append(Episode(data=ep,
                                        podcast=podcast,
                                        api=self))
        return episodes

    def _make_categories(self, json_data: dict) -> List[Category]:
        categories = []
        if json_data:
            for cat in json_data:
                categories.append(Category(data=cat,
                                           api=self))
        return categories

    @property
    def account(self) -> Account:
        url = _make_url(base=self._api_base,
                        endpoint="/subscription/status")
        data = self._get_json(url=url,
                              include_token=True)
        return Account(data=data,
                       api=self)

    @property
    def stats(self) -> dict:
        endpoint = _get_endpoint("stats")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        return self._post_json(url=url)

    @property
    def subscriptions(self) -> List[Podcast]:
        endpoint = _get_endpoint("list")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url,
                               data={'v': 1})
        return self._make_podcasts(json_data=data)

    @property
    def in_progress(self) -> List[Episode]:
        endpoint = _get_endpoint("in_progress")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def up_next(self) -> List[Episode]:
        endpoint = _get_endpoint("up_next")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url,
                               data={'version': 2,
                                     'model': 'webplayer'})
        return self._make_episodes(json_data=data,
                                   podcast=None)

    @property
    def starred(self) -> List[Episode]:
        endpoint = _get_endpoint("starred")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def history(self) -> List[Episode]:
        endpoint = _get_endpoint("history")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def new_releases(self) -> List[Episode]:
        endpoint = _get_endpoint("new_releases")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def recommendations(self) -> List[Episode]:
        endpoint = _get_endpoint("recommendations")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    def search(self, keyword: str) -> List[Podcast]:
        endpoint = _get_endpoint("search")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url,
                               data={"term": keyword})
        return self._make_podcasts(json_data=data)

    @property
    def categories(self) -> List[Category]:
        data = self._get_json(url="https://static.pocketcasts.com/discover/json/categories_v2.json")
        return self._make_categories(json_data=data)

    def category(self, category_name: str) -> Union[Category, None]:
        for category in self.categories:
            if category.name.lower() == category_name.lower():
                return category
        return None

    @property
    def trending(self) -> List[Podcast]:
        endpoint = _get_endpoint("trending")
        url = _make_url(base=self._lists_base,
                        endpoint=endpoint,
                        suffix=".json")
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def popular(self) -> List[Podcast]:
        endpoint = _get_endpoint("popular")
        url = _make_url(base=self._lists_base,
                        endpoint=endpoint,
                        suffix=".json")
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def featured(self) -> List[Podcast]:
        endpoint = _get_endpoint("featured")
        url = _make_url(base=self._lists_base,
                        endpoint=endpoint,
                        suffix=".json")
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def networks(self):
        return []

    def content(self, list_id: str) -> List[Podcast]:
        url = f"https://lists.pocketcasts.com/{list_id}.json"
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)
