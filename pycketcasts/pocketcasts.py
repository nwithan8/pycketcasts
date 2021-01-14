from datetime import datetime
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
    'episode_star': 'sync/update_episode_star',
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
        """
        Interact with a specific podcast episode

        :param data: JSON data for episode
        :type data: dict
        :param podcast: Podcast that the episode belongs to
        :type podcast: Podcast
        :param api: PocketCasts API object
        :type api: PocketCast
        """
        self._data = data
        self._podcast = podcast
        if not self._podcast:
            self._podcast = api.get_podcast_by_id(podcast_id=self.podcast_id)
        self._api = api

    @property
    def podcast(self):
        """
        Get episode's corresponding podcast

        :rtype: Podcast
        """
        if not self._podcast:
            self._podcast = self._api.get_podcast_by_id(podcast_id=self.podcast_id)
        return self._podcast

    @property
    def title(self) -> str:
        """
        Get episode title

        :rtype: str
        """
        return self._data.get('title')

    @property
    def id(self) -> str:
        """
        Get episode ID

        :rtype: str
        """
        return self._data.get('uuid')

    @property
    def duration(self) -> int:
        """
        Get episode duration

        :rtype: int
        """
        return self._data.get('duration')

    @property
    def published_date(self) -> Union[datetime, None]:
        """
        Get episode's publication date

        :rtype: datetime.datetime
        """
        try:
            return datetime.strptime(self._data.get('published'), 'YYYY-MM-DDTHH:mm:ssZ')
        except:
            return None

    @property
    def url(self) -> str:
        """
        Get episode url

        :rtype: str
        """
        return self._data.get('url')

    @property
    def playing(self) -> bool:
        """
        Get episode playing status

        :rtype: bool
        """
        return True if self._data.get('playing_status') > 0 else False

    @property
    def size(self) -> int:
        """
        Get episode size

        :rtype: int
        """
        return self._data.get('size')

    @property
    def file_type(self) -> str:
        """
        Get episode file type

        :rtype: str
        """
        return self._data.get('fileType')

    @property
    def type(self) -> str:
        """
        Get episode type

        :rtype: str
        """
        return self._data.get('episodeType')

    @property
    def season(self) -> int:
        """
        Get episode season

        :rtype: int
        """
        return self._data.get('episodeSeason')

    @property
    def number(self) -> int:
        """
        Get episode number

        :rtype: int
        """
        return self._data.get('episodeNumber')

    @property
    def current_position(self) -> int:
        """
        Get episode current position

        :rtype: int
        """
        return self._data.get('playedUpTo')

    @property
    def deleted(self) -> bool:
        """
        Get whether the episode is deleted

        :rtype: bool
        """
        return self._data.get('isDeleted')

    @property
    def starred(self) -> bool:
        """
        Get whether episode is starred

        :rtype: bool
        """
        return self._data.get('starred')

    @property
    def podcast_id(self) -> str:
        """
        Get ID of corresponding podcast

        :rtype: str
        """
        return self._data.get('podcastUuid')

    @property
    def podcast_title(self) -> str:
        """
        Get title of corresponding podcast

        :rtype: str
        """
        return self._data.get('podcastTitle')

    @property
    def show_notes(self) -> str:
        """
        Get the show notes for the episode

        :return: show notes
        :rtype: str
        """
        url = f"https://podcast-api.pocketcasts.com/episode/show_notes/{self.id}"
        print(url)
        data = self._api._get_json(url=url, include_token=True)
        return data.get('show_notes', "")

    def mark_played(self) -> bool:
        """
        Mark this episode as played

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("play_status")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.id,
                                 'podcast': self.podcast_id if self.podcast_id else self.podcast.id,
                                 'status': 3
                                 }
                           ):
            return True
        return False

    def mark_unplayed(self) -> bool:
        """
        Mark this episode as unplayed

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("play_status")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.id,
                                 'podcast': self.podcast_id if self.podcast_id else self.podcast.id,
                                 'status': 1,
                                 'position': 0
                                 }
                           ):
            return True
        return False

    def add_star(self) -> bool:
        """
        Add a star to this episode

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("episode_star")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           json={"uuid": self.id,
                                 "podcast": self.podcast_id if self.podcast_id else self.podcast.id,
                                 "star": True}
                           ):
            return True
        return False

    def remove_star(self) -> bool:
        """
        Remove a star from this episode

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("episode_star")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           json={"uuid": self.id,
                                 "podcast": self.podcast_id if self.podcast_id else self.podcast.id,
                                 "star": False}
                           ):
            return True
        return False

    def archive(self) -> bool:
        """
        Archive this episode

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("episode_archive")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           data={'episodes': [
                               {'uuid': self.id,
                                'podcast': self.podcast_id if self.podcast_id else self.podcast.id
                                }
                           ],
                               'archive': True}):
            return True
        return False

    def unarchive(self) -> bool:
        """
        Unarchive this episode

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("episode_archive")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'episodes': [
                               {'uuid': self.id,
                                'podcast': self.podcast_id if self.podcast_id else self.podcast.id
                                }
                           ],
                               'archive': False}):
            return True
        return False

    def play_next(self) -> bool:
        """
        Add this episode to the front of the "Play Next" queue

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("play_next")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           data={'version': 2,
                                 'episode': {'uuid': self.id,
                                             'title': self.title,
                                             'url': self.url,
                                             'podcast': self.podcast_id if self.podcast_id else self.podcast.id,
                                             'published': self.published_date
                                             }
                                 }
                           ):
            return True
        return False

    def play_last(self) -> bool:
        """
        Add this episode to the end of the "Play Next" queue

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("play_last")
        url = _make_url(base=self._api._api_base, endpoint=endpoint)
        if self._api._post(url=url,
                           data={'version': 2,
                                 'episode': {'uuid': self.id,
                                             'title': self.title,
                                             'url': self.url,
                                             'podcast': self.podcast_id if self.podcast_id else self.podcast.id,
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
        """
        Interact with a specific podcast

        :param data: JSON data for podcast
        :type data: dict
        :param api: PocketCasts API object
        :type api: PocketCast
        """
        self._data = data
        self._api = api

    @property
    def title(self) -> str:
        """
        Get podcast title

        :rtype: str
        """
        return self._data.get('title')

    @property
    def author(self) -> str:
        """
        Get podcast author

        :rtype: str
        """
        return self._data.get('author')

    @property
    def description(self) -> str:
        """
        Get podcast description

        :rtype: str
        """
        return self._data.get('description')

    @property
    def feed(self) -> str:
        """
        Get podcast RSS feed

        :rtype: str
        """
        return self._data.get('feed')

    @property
    def id(self) -> str:
        """
        Get podcast ID

        :rtype: str
        """
        return self._data.get('uuid')

    @property
    def itunes(self) -> str:
        """
        Get podcast iTunes ID

        :rtype: str
        """
        return self._data.get('itunes')

    @property
    def website(self) -> str:
        """
        Get podcast website URL

        :rtype: str
        """
        return self._data.get('website')

    @property
    def episodes(self) -> List[Episode]:
        """
        Get this podcast's episodes

        :return: List of episodes
        :rtype: list[Episode]
        """
        endpoint = _get_endpoint("episodes")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        data = self._api._post_json(url=url,
                                    data={'uuid': self.id})
        return self._api._make_episodes(json_data=data,
                                        podcast=self)

    def subscribe(self) -> bool:
        """
        Subscribe to this podcast

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("subscribe")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.id}):
            return True
        return False

    def unsubscribe(self) -> bool:
        """
        Unsubscribe to this podcast

        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        endpoint = _get_endpoint("unsubscribe")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.id}):
            return True
        return False


class Category:
    def __init__(self, data: dict, api):
        """
        Interact with a PocketCasts category

        :param data: JSON data for category
        :type data: dict
        :param api: PocketCasts API object
        :type api: PocketCast
        """
        self._data = data
        self._api = api

    @property
    def name(self) -> str:
        """
        Get category name

        :rtype: str
        """
        return self._data.get('name')

    @property
    def icon(self) -> str:
        """
        Get category icon URL

        :rtype: str
        """
        return self._data.get('icon')

    @property
    def source(self) -> str:
        """
        Get category source

        :rtype: str
        """
        return self._data.get('source')

    def get_podcasts(self, region: str = 'us') -> List[Podcast]:
        """
        Get podcasts in this category

        :param region: Region for the category (default: 'us')
        :type region: str
        :return: list of podcasts
        :rtype: list[Podcast]
        """
        url = self.source.replace('[regionCode]', region)
        data = self._api._get_json(url=url)
        return self._api._make_podcasts(json_data=data)


class Account:

    def __init__(self, data: dict, api):
        self._data = data
        self._api = api

    @property
    def paid(self) -> bool:
        """
        Get whether this account if Premium

        :rtype: bool
        """
        return True if self._data.get('paid') == 1 else False

    @property
    def platform(self) -> str:
        """
        Get account platform

        :rtype: str
        """
        return self._data.get('platform')

    @property
    def expiry_date(self) -> str:
        """
        Get expiry date

        :rtype: str
        """
        return self._data.get('expiryDate')

    @property
    def auto_renewing(self) -> str:
        """
        Get auto-renewing status

        :rtype: str
        """
        return self._data.get('autoRenewing')

    @property
    def gift_days(self) -> int:
        """
        Get gift days

        :rtype: int
        """
        return self._data.get('giftDays')

    @property
    def cancel_url(self) -> str:
        """
        Get URL to cancel account

        :rtype: str
        """
        return self._data.get('cancelUrl')

    @property
    def update_url(self) -> str:
        """
        Get URL to update account

        :rtype: str
        """
        return self._data.get('updateURL')

    @property
    def frequency(self) -> str:
        """
        Get frequency

        :rtype: str
        """
        return self._data.get('frequency')

    @property
    def web(self) -> str:
        """
        Get web URL

        :rtype: str
        """
        return self._data.get('web')


class PocketCast:
    def __init__(self, email: str, password: str):
        """
        Interact with the PocketCasts API

        :param email: Your PocketCasts email address
        :type email: str
        :param password: Your PocketCasts password
        :type password: str
        """
        self._api_base = "https://api.pocketcasts.com"
        self._lists_base = "https://lists.pocketcasts.com"
        self._email = email
        self._password = password
        self._token = None
        self._session = requests.Session()
        self._login()

    def _login(self):
        """
        Login to your PocketCasts account to get an auth token

        :return: None
        :rtype: None
        """
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
        """
        Send a GET request to the PocketCasts API

        :param url: API endpoint
        :type url: str
        :param params: GET request parameters
        :type params: dict
        :param include_token: Whether to include the auth token (default: False)
        :type include_token: bool
        :return: API response
        :rtype: requests.Response
        """
        response = self._session.get(url=url,
                                     params=params,
                                     headers=({'Authorization': f'Bearer {self._token}'}
                                              if include_token else None))
        return response

    def _post(self,
              url: str,
              params: dict = None,
              data: dict = None,
              json: dict = None) -> requests.Response:
        """
        Send a POST request to the PocketCasts API

        :param url: API endpoint
        :type url: str
        :param params: POST request parameters
        :type params: dict
        :param data: POST request body
        :type data: dict
        :param json: POST request JSON body
        :type json: dict
        :return: API response
        :rtype: requests.Response
        """
        header = {'Authorization': f'Bearer {self._token}'} if self._token else None
        response = self._session.post(url=url,
                                      params=params,
                                      data=data,
                                      json=json,
                                      headers=header)
        return response

    def _get_json(self,
                  url: str,
                  params: dict = None,
                  include_token: bool = False) -> dict:
        """
        Get JSON from a GET request to PocketCasts API

        :param url: API endpoint
        :type url: str
        :param params: GET request parameters
        :type params: dict
        :param include_token: Whether to include the auth token (default: False)
        :type include_token: bool
        :return: JSON data
        :rtype: dict
        """
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
        """
        Get JSON from a POST request to PocketCasts API

        :param url: API endpoint
        :type url: str
        :param params: POST request parameters
        :type params: dict
        :param data: POST request body
        :type data: dict
        :param json: POST request JSON body
        :type json: dict
        :return: JSON data
        :rtype: dict
        """
        res = self._post(url=url,
                         params=params,
                         data=data,
                         json=json)
        if res:
            return res.json()
        return {}

    def _make_podcast(self,
                      json_data: dict) -> Podcast:
        """
        Construct a ``Podcast`` object from JSON data

        :param json_data: Podcast JSON data
        :type json_data: dict
        :return: Podcast objects
        :rtype: Podcast
        """
        return Podcast(data=json_data['podcast'], api=self)

    def _make_podcasts(self,
                       json_data: dict) -> List[Podcast]:
        """
        Construct ``Podcast`` objects from JSON data

        :param json_data: Podcasts JSON data
        :type json_data: dict
        :return: list of Podcast objects
        :rtype: list[Podcast]
        """
        podcasts = []
        if json_data and json_data.get('podcasts'):
            for pod in json_data['podcasts']:
                podcasts.append(Podcast(data=pod, api=self))
        return podcasts

    def _make_episodes(self,
                       json_data: dict,
                       podcast: Podcast = None) -> List[Episode]:
        """
        Construct ``Episode`` objects from JSON data

        :param json_data: Episodes JSON data
        :type json_data: dict
        :return: list of Episode objects
        :rtype: list[Episode]
        """
        episodes = []
        if json_data and json_data.get('episodes'):
            for ep in json_data['episodes']:
                episodes.append(Episode(data=ep,
                                        podcast=podcast,
                                        api=self))
        return episodes

    def _make_categories(self, json_data: dict) -> List[Category]:
        """
        Construct ``Category`` objects from JSON data

        :param json_data: Categories JSON data
        :type json_data: dict
        :return: list of Category objects
        :rtype: list[Category]
        """
        categories = []
        if json_data:
            for cat in json_data:
                categories.append(Category(data=cat,
                                           api=self))
        return categories

    @property
    def account(self) -> Account:
        """
        Get your PocketCasts user account

        :return: PocketCasts user account
        :rtype: Account
        """
        url = _make_url(base=self._api_base,
                        endpoint="/subscription/status")
        data = self._get_json(url=url,
                              include_token=True)
        return Account(data=data,
                       api=self)

    @property
    def stats(self) -> dict:
        """
        Get PocketCasts statistics

        :return: dictionary of statistics
        :rtype: dict
        """
        endpoint = _get_endpoint("stats")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        return self._post_json(url=url)

    @property
    def subscriptions(self) -> List[Podcast]:
        """
        Get your PocketCasts podcast subscriptions

        :return: list of podcasts
        :rtype: list[Podcast]
        """
        endpoint = _get_endpoint("list")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url,
                               data={'v': 1})
        return self._make_podcasts(json_data=data)

    @property
    def in_progress(self) -> List[Episode]:
        """
        Get your in-progress podcast episodes

        :return: list of episodes
        :rtype: list[Episode]
        """
        endpoint = _get_endpoint("in_progress")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def up_next(self) -> List[Episode]:
        """
        Get the podcast episodes in your queue

        :return: list of episodes
        :rtype: list[Episode]
        """
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
        """
        Get your starred podcast episodes

        :return: list of episodes
        :rtype: list[Episode]
        """
        endpoint = _get_endpoint("starred")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def history(self) -> List[Episode]:
        """
        Get your podcast episode history

        :return: list of episodes
        :rtype: list[Episode]
        """
        endpoint = _get_endpoint("history")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def new_releases(self) -> List[Episode]:
        """
        Get newly-released podcast episodes

        :return: list of episodes
        :rtype: list[Episode]
        """
        endpoint = _get_endpoint("new_releases")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    @property
    def recommendations(self) -> List[Episode]:
        """
        Get recommended podcast episodes

        :return: list of episodes
        :rtype: list[Episode]
        """
        endpoint = _get_endpoint("recommendations")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        return self._make_episodes(json_data=data)

    def get_podcast_by_id(self, podcast_id: str) -> Union[Podcast, None]:
        """
        Get a podcast by its ID

        :param podcast_id: ID of podcast
        :type podcast_id: str
        :return: Podcast or None if not found
        :rtype: Podcast
        """
        url = f"https://podcast-api.pocketcasts.com/podcast/full/{podcast_id}"
        data = self._get_json(url=url)
        if data and data.get('podcast'):
            return self._make_podcast(json_data=data)
        return None

    def search(self, keyword: str) -> List[Podcast]:
        """
        Search for podcasts by a keyword

        :param keyword: keyword to use in search
        :type keyword: str
        :return: list of podcasts from search
        :rtype: list[Podcast]
        """
        endpoint = _get_endpoint("search")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url,
                               data={"term": keyword})
        return self._make_podcasts(json_data=data)

    @property
    def categories(self) -> List[Category]:
        """
        Get the available PocketCasts categories

        :return: list of available categories
        :rtype: list[Category]
        """
        data = self._get_json(url="https://static.pocketcasts.com/discover/json/categories_v2.json")
        return self._make_categories(json_data=data)

    def category(self, category_name: str) -> Union[Category, None]:
        """
        Get a category by name

        :param category_name: name of PocketCasts category
        :type category_name: str
        :return: Either a matching category or None if not found
        :rtype: Category
        """
        for category in self.categories:
            if category.name.lower() == category_name.lower():
                return category
        return None

    @property
    def trending(self) -> List[Podcast]:
        """
        Get trending podcasts

        :return: list of trending podcasts
        :rtype: list[Podcast]
        """
        endpoint = _get_endpoint("trending")
        url = _make_url(base=self._lists_base,
                        endpoint=endpoint,
                        suffix=".json")
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def popular(self) -> List[Podcast]:
        """
        Get popular podcasts

        :return: list of popular podcasts
        :rtype: list[Podcast]
        """
        endpoint = _get_endpoint("popular")
        url = _make_url(base=self._lists_base,
                        endpoint=endpoint,
                        suffix=".json")
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def featured(self) -> List[Podcast]:
        """
        Get featured podcasts

        :return: list of featured podcasts
        :rtype: list[Podcast]
        """
        endpoint = _get_endpoint("featured")
        url = _make_url(base=self._lists_base,
                        endpoint=endpoint,
                        suffix=".json")
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)

    @property
    def networks(self):
        """
        Get available podcast networks

        :return: list of available podcast networks
        :rtype: list
        """
        return []

    def content(self, list_id: str) -> List[Podcast]:
        """
        Get a list of podcasts by a list ID

        :param list_id: ID of list
        :type list_id: str
        :return: list of podcasts
        :rtype: list[Podcast]
        """
        url = f"https://lists.pocketcasts.com/{list_id}.json"
        data = self._get_json(url=url)
        return self._make_podcasts(json_data=data)
