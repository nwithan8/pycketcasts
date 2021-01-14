from datetime import datetime
from typing import List, Union
import ntpath
import magic
import os

import requests

endpoints = {
    'login': 'user/login',
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
    'episode': 'user/podcast/episode',
    'episodes': 'user/podcast/episodes',
    'subscribe': 'user/podcast/subscribe',
    'unsubscribe': 'user/podcast/unsubscribe',
    'episode_archive': 'sync/update_episode_archive',
    'episode_star': 'sync/update_episode_star',
    'up_next': 'up_next/list',
    'play_status': 'sync/update_episode',
    'play_next': 'up_next/play_next',
    'play_last': 'up_next/play_last',
    'share': 'podcasts/share_link',
    'account': 'subscription/status',
    'upload': 'files/upload/request',
    'files': 'files'
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
    def share_link(self) -> Union[str, None]:
        """
        Get share link for this episode

        :return: share link
        :rtype: str
        """
        endpoint = _get_endpoint("share")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        data = self._api._post_json(url=url,
                                    data={'episode': self.id,
                                          'podcast': self.podcast_id})
        if data:
            return data.get('url')
        return None

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
        return self._data.get('podcastUuid') if self._data.get('podcastUuid') else self.podcast.id

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

    def update_progress(self, progress: int) -> bool:
        """
        Update progress in this episode

        :param progress: Episode progress in seconds
        :type progress: int
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if progress > self.duration:
            raise Exception("Cannot update with progress longer than episode duration")
        endpoint = _get_endpoint("play_status")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        if self._api._post(url=url,
                           data={'uuid': self.id,
                                 'podcast': self.podcast_id,
                                 'status': 2,
                                 'position': progress
                                 }
                           ):
            return True
        return False

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
                                 'podcast': self.podcast_id,
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
                                 'podcast': self.podcast_id,
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
                                 "podcast": self.podcast_id,
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
                                 "podcast": self.podcast_id,
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
                                'podcast': self.podcast_id
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
                                'podcast': self.podcast_id
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
                                             'podcast': self.podcast_id,
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
                                             'podcast': self.podcast_id,
                                             'published': self.published_date
                                             }
                                 }
                           ):
            return True
        return False


class Podcast:
    def __init__(self, data: dict, api, extended_json: dict = {}, full_item: bool = False):
        """
        Interact with a specific podcast

        :param data: JSON data for podcast
        :type data: dict
        :param api: PocketCasts API object
        :type api: PocketCast
        """
        self._data = data
        self._api = api
        self._extended_json = extended_json
        self._full_item = full_item

    def _get_full_podcast_object(self):
        """
        Reload this Podcast object with all data

        :return: None
        :rtype: None
        """
        data = self._api._get_podcast_data_by_id(podcast_id=self.id)
        self.__init__(data=data, api=self._api, full_item=True)

    def get_episode_by_id(self, episode_id: str) -> Union[Episode, None]:
        """
        Get an episode of this podcast by its ID

        :param episode_id: ID of episode
        :type episode_id: str
        :return: Episode object or None if not found
        :rtype: Episode
        """
        return self._api.get_episode_by_id(episode_id=episode_id, podcast_id=self.id)

    @property
    def share_link(self) -> Union[str, None]:
        """
        Get share link for this podcast

        :return: share link
        :rtype: str
        """
        endpoint = _get_endpoint("share")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        data = self._api._post_json(url=url,
                                    data={'episode': "",
                                          'podcast': self.id})
        if data:
            return data.get('url')
        return None

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
    def episode_frequency(self) -> str:
        """
        Get episode frequency

        :rtype: str
        """
        return self._extended_json.get('episode_frequency')

    @property
    def next_episode_date(self) -> Union[datetime, None]:
        """
        Estimated date for next episode

        :rtype: datetime.datetime
        """
        date = self._extended_json.get('estimated_next_episode_at')
        if not date:
            return None
        return datetime.strptime(date_string=date, format="YYYY-MM-DDTHH:mm:ssZ")

    @property
    def has_seasons(self) -> bool:
        """
        Get whether the podcast has seasons

        :rtype: bool
        """
        return self._extended_json.get('has_seasons')

    @property
    def season_count(self) -> int:
        """
        Get podcast season count

        :rtype: int
        """
        return self._extended_json.get('season_count')

    @property
    def episode_count(self) -> int:
        """
        Get podcast episode count

        :rtype: int
        """
        return self._extended_json.get('episode_count')

    @property
    def has_more_episodes(self) -> bool:
        """
        Get whether the podcast has more episodes

        :rtype: bool
        """
        return self._extended_json.get('has_more_episodes')

    @property
    def category_name(self) -> str:
        """
        Get podcast category name

        :rtype: str
        """
        return self._data.get('category')

    @property
    def category(self):
        """
        Get podcast category

        :rtype: Category
        """
        if self.category_name:
            return self._api.category(category_name=self.category_name)
        return None

    @property
    def is_audio(self) -> bool:
        """
        Get whether the podcast is audio

        :rtype: bool
        """
        return self._data.get('audio', True)

    @property
    def show_type(self) -> str:
        """
        Get podcast show type (i.e. episodic)

        :rtype: str
        """
        return self._data.get('show_type')

    @property
    def paid(self) -> bool:
        """
        Get whether the podcast is paid

        :rtype: bool
        """
        return False if self._data.get('paid', 0) == 0 else True

    @property
    def licensing(self) -> bool:
        """
        Get whether the podcast is licensed

        :rtype: bool
        """
        return False if self._data.get('paid', 0) == 0 else True

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


class Stats:
    def __init__(self, data: dict):
        """
        Interact with your PocketCasts statistics

        :param data: JSON data for statistics
        :type data: dict
        """
        self._data = data

    @property
    def silence_time_removed(self) -> int:
        """
        Get how many seconds of silence have been removed

        :rtype: int
        """
        return int(self._data.get('timeSilenceRemoval'))

    @property
    def time_skipped(self) -> int:
        """
        Get how many seconds you have skipped

        :rtype: int
        """
        return int(self._data.get('timeSkipping'))

    @property
    def intro_time_skipped(self) -> int:
        """
        Get how many seconds of intro you have skipped

        :rtype: int
        """
        return int(self._data.get('timeIntroSkipping'))

    @property
    def time_variable_speed(self) -> int:
        """
        Get how many seconds you have used variable speed

        :rtype: int
        """
        return int(self._data.get('timeVariableSpeed'))

    @property
    def time_listened(self) -> int:
        """
        Get how many seconds you have listened

        :rtype: int
        """
        return int(self._data.get('timeListened'))

    @property
    def starting_date(self) -> Union[datetime, None]:
        """
        Get when these stats started

        :rtype: datetime.datetime
        """
        date = self._data.get('timesStartedAt')
        if not date:
            return None
        return datetime.strptime(date_string=date, format="YYYY-MM-DDTHH:mm:ssZ")


class Subscription:
    def __init__(self, data: dict):
        """
        Interact with a PocketCasts subscription

        :param data: JSON data from subscription
        :type data: dict
        """
        self._data = data

    @property
    def platform(self) -> int:
        """
        Get account platform

        :rtype: int
        """
        return self._data.get('platform')

    @property
    def type(self) -> int:
        """
        Get account type

        :rtype: int
        """
        return self._data.get('type')

    @property
    def frequency(self) -> int:
        """
        Get account frequency

        :rtype: int
        """
        return self._data.get('frequency')

    @property
    def auto_renewing(self) -> bool:
        """
        Get auto-renewing status

        :rtype: bool
        """
        return self._data.get('autoRenewing')

    @property
    def expiry_date(self) -> Union[datetime, None]:
        """
        Get expiry date

        :rtype: datetime.datetime
        """
        date = self._data.get('expiryDate')
        if not date:
            return None
        return datetime.strptime(date_string=date, format="YYYY-MM-DDTHH:mm:ssZ")

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
    def plan(self) -> str:
        """
        Get account plan type

        :rtype: str
        """
        return self._data.get('plan')

    @property
    def index(self) -> int:
        """
        Get account index

        :rtype: int
        """
        return self._data.get('index')

    @property
    def gift_days(self) -> int:
        """
        Get gift days

        :rtype: int
        """
        return self._data.get('giftDays')

    @property
    def paid(self) -> bool:
        """
        Get whether this account if Premium

        :rtype: bool
        """
        return True if self._data.get('paid') == 1 else False

    @property
    def web_status(self) -> int:
        """
        Get account web status

        :rtype: int
        """
        return self._data.get('webStatus')

    @property
    def bundle_id(self) -> str:
        """
        Get account bundle ID

        :rtype: str
        """
        return self._data.get('bundleUuid')


class File:
    def __init__(self, data: dict):
        self._data = data

    def delete(self) -> bool:
        endpoint = f"{self._api._api_base}/files/{self.id}"
        res = self._api._delete(url=endpoint)
        if res:
            return True
        return False

    def update(self, name: str = None, colour: int = None) -> bool:
        data = {
            'uuid': self.id,
            'title': name if name else self.title,
            'colour': colour if colour else self.colour
        }
        endpoint = _get_endpoint('files')
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        res = self._api._post(url=url,
                              data=data)
        if res:
            return True
        return False

    # TODO Download file

    # TODO Play next

    # TODO Play last

    # TODO Mark as played

    # TODO Mark as unplayed

    @property
    def id(self) -> str:
        return self._data.get('uuid')

    @property
    def title(self) -> str:
        return self._data.get('title')

    @property
    def size(self) -> int:
        return int(self._data.get('size'))

    @property
    def content_type(self) -> str:
        return self._data.get('contentType')

    @property
    def progress(self) -> int:
        return int(self._data.get('playedUpTo'))

    @property
    def progress_modified(self) -> str:
        return int(self._data.get('playedUpToModified'))

    @property
    def duration(self) -> int:
        return int(self._data.get('duration'))

    @property
    def published(self) -> Union[datetime, None]:
        date = self._data.get('published')
        if not date:
            return None
        return datetime.strptime(date_string=date, format="YYYY-MM-DDTHH:mm:ssZ")

    @property
    def colour(self) -> int:
        return int(self._data.get('colour'))

    @property
    def image_url(self) -> str:
        return self._data.get('imageUrl')

    @property
    def has_custom_image(self) -> bool:
        return self._data.get('hasCustomImage')

    @property
    def modified_at(self) -> Union[datetime, None]:
        date = self._data.get('modifiedAt')
        if not date:
            return None
        return datetime.strptime(date_string=date, format="YYYY-MM-DDTHH:mm:ssZ")

    @property
    def image_status(self) -> int:
        return self._data.get('imageStatus')


class Account:

    def __init__(self, data: dict, api):
        self._data = data
        self._api = api

    @property
    def subscriptions(self) -> List[Subscription]:
        """
        Get your PocketCasts subscriptions

        :return: list of PocketCasts subscriptions
        :rtype: list[Subscription]
        """
        subscriptions = []
        for sub in self._data.get('subscriptions', []):
            subscriptions.append(Subscription(data=sub))
        return subscriptions

    @property
    def web(self) -> dict:
        """
        Get web info

        :rtype: dict
        """
        return self._data.get('web')

    @property
    def _account_file_details(self) -> dict:
        endpoint = _get_endpoint('files')
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        res = self._api._get_json(url, include_token=True)
        return res

    @property
    def account_file_details(self) -> Union[dict, None]:
        res = self._account_file_details
        if res:
            return res.get('account')
        return None

    @property
    def files(self) -> List[File]:
        res = self._account_file_details
        files = []
        for file in res.get('files', []):
            files.append(File(data=file))
        return files

    def upload_file(self, file_path: str) -> bool:
        """
        Upload a file to PocketCasts

        :param file_path: path of file to upload
        :type file_path: str
        :return: True if successful, False if unsuccessful
        :rtype: bool
        """
        if not os.path.exists(file_path):
            raise Exception("File does not exist.")
        endpoint = _get_endpoint("upload")
        url = _make_url(base=self._api._api_base,
                        endpoint=endpoint)
        file_name = ntpath.basename(file_path)
        mime_type = magic.Magic(mime=True).from_file(filename=file_path)
        file_size = os.path.getsize(file_path)
        res = self._api._post(url,
                              data={
                                  'title': file_name,
                                  'contentType': 'audio/mpeg',
                                  'hasCustomImage': False,
                                  'size': file_size
                              },
                              files={file_name: open(file_path, 'rb')})
        if res:
            return True
        return False


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
        endpoint = _get_endpoint('login')
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
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
              json: dict = None,
              files: dict = None) -> requests.Response:
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
        :param files: Files to send with POST request
        :type files: dict
        :return: API response
        :rtype: requests.Response
        """
        header = {'Authorization': f'Bearer {self._token}'} if self._token else None
        response = self._session.post(url=url,
                                      params=params,
                                      data=data,
                                      json=json,
                                      files=files,
                                      headers=header)
        return response

    def _delete(self,
              url: str,
              params: dict = None,
              data: dict = None,
              json: dict = None,
              files: dict = None) -> requests.Response:
        """
        Send a DELETE request to the PocketCasts API

        :param url: API endpoint
        :type url: str
        :param params: DELETE request parameters
        :type params: dict
        :param data: POST request body
        :type data: dict
        :param json: DELETE request JSON body
        :type json: dict
        :param files: Files to send with DELETE request
        :type files: dict
        :return: API response
        :rtype: requests.Response
        """
        header = {'Authorization': f'Bearer {self._token}'} if self._token else None
        response = self._session.delete(url=url,
                                        params=params,
                                        data=data,
                                        json=json,
                                        files=files,
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
        :return: Podcast object
        :rtype: Podcast
        """
        if json_data.get('podcast'):
            return Podcast(data=json_data['podcast'], extended_json=json_data, api=self)
        return Podcast(data=json_data, api=self)

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
                podcasts.append(self._make_podcast(json_data=pod))
        return podcasts

    def _make_episode(self,
                      json_data: dict,
                      podcast: Podcast = None) -> Episode:
        """
        Construct an ``Episode`` object from JSON data

        :param json_data: Episode JSON data
        :type json_data: dict
        :return: Episode object
        :rtype: Episode
        """
        if json_data.get('episode'):
            json_data = json_data['episode']
        return Episode(data=json_data, podcast=podcast, api=self)

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
                episodes.append(self._make_episode(json_data=ep, podcast=podcast))
        return episodes

    def _make_category(self, json_data: dict) -> Category:
        """
        Construct a ``Category`` object from JSON data

        :param json_data: Category JSON data
        :type json_data: dict
        :return: Category object
        :rtype: Category
        """
        return Category(data=json_data, api=self)

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
                categories.append(self._make_category(json_data=json_data))
        return categories

    @property
    def account(self) -> Account:
        """
        Get your PocketCasts user account

        :return: PocketCasts user account
        :rtype: Account
        """
        endpoint = _get_endpoint("account")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._get_json(url=url,
                              include_token=True)
        return Account(data=data,
                       api=self)

    @property
    def stats(self) -> Union[Stats, None]:
        """
        Get PocketCasts statistics

        :return: dictionary of statistics
        :rtype: dict
        """
        endpoint = _get_endpoint("stats")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url)
        if data:
            return Stats(data=data)
        return None

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

    def _get_podcast_data_by_id(self, podcast_id: str) -> dict:
        """
        Get a podcast's data by its ID

        :param podcast_id: ID of podcast
        :type podcast_id: str
        :return: JSON data
        :rtype: dict
        """
        url = f"https://podcast-api.pocketcasts.com/podcast/full/{podcast_id}"
        data = self._get_json(url=url)
        return data

    def get_podcast_by_id(self, podcast_id: str) -> Union[Podcast, None]:
        """
        Get a podcast by its ID

        :param podcast_id: ID of podcast
        :type podcast_id: str
        :return: Podcast or None if not found
        :rtype: Podcast
        """
        data = self._get_podcast_data_by_id(podcast_id=podcast_id)
        if data and data.get('podcast'):
            return self._make_podcast(json_data=data)
        return None

    def _get_episode_data_by_id(self, episode_id: str, podcast_id: str) -> dict:
        """
        Get an episode's data by its ID

        :param episode_id: ID of episode
        :type episode_id: str
        :param podcast_id: ID of podcast
        :type podcast_id: str
        :return: JSON data
        :rtype: dict
        """
        endpoint = _get_endpoint("episode")
        url = _make_url(base=self._api_base,
                        endpoint=endpoint)
        data = self._post_json(url=url,
                               data={'uuid': episode_id,
                                     'podcast': podcast_id}
                               )
        return data

    def get_episode_by_id(self, episode_id: str, podcast_id: str) -> Union[Episode, None]:
        """
        Get an episode by its ID

        :param episode_id: ID of episode
        :type episode_id: str
        :param podcast_id: ID of podcast
        :type podcast_id: str
        :return: JSON data
        :rtype: dict
        """
        data = self._get_episode_data_by_id(episode_id=episode_id, podcast_id=podcast_id)
        if data:
            podcast = self.get_podcast_by_id(podcast_id=podcast_id)
            return self._make_episode(json_data=data, podcast=podcast)
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
