'''Module for holding application models.'''
from collections import deque

import datetime
import requests

from src.global_constants import __debugflg__

from core.odno_logging import odnologger
from exceptions.odno_exceptions import OdnoException

class Song:
    '''
        Model-Object representing audio file in an album.
    '''
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', "")
        self.artist = kwargs.get('artist', "")
        self.album = kwargs.get('album', "")
        self.album_artist = kwargs.get("album_artist", "")
        self.cd = kwargs.get('cd', 1)
        self.genre = kwargs.get('genre', "")
        self.year = kwargs.get('year', datetime.datetime.strptime("1970-01-01", "%Y-%m-%d"))
        self.track_num = kwargs.get('track_num', 0)
        self.cover = kwargs.get('cover', "")

    def __str__(self):
        return f"{self.title} : [artist={self.artist}, album={self.album}, genre={self.genre}, cd={self.cd}, year={self.year}, track_num={self.track_num}, album_cover={self.cover}]"

    def __repr__(self):
        return self.__str__()

class SongBuilder:
    ''' 
        Song self. 
        Returns an instance of Song when build is invoked.
    '''
    def __init__(self):
        self._params = {}

    def title(self, title):
        '''Title of the track string'''
        self._params['title'] = title
        return self

    def artist(self, artist):
        '''Name of the artist string'''
        self._params['artist'] = artist
        return self

    def album(self, album):
        '''Name of the albume string'''
        self._params['album'] = album
        return self

    def album_artist(self, album_artist):
        '''Name of the album artist string'''
        self._params['album_artist'] = album_artist
        return self

    def cd(self, cd):
        '''CD number/Disc number'''
        self._params['cd'] = cd
        return self

    def genre(self, genre):
        '''genre of the album'''
        self._params['genre'] = genre
        return self

    def year(self, year):
        '''datetime release date/year'''
        if not isinstance(year, datetime.datetime) and year not in "N/A":
            raise TypeError("year value must be expressed as datetime.")

        self._params['year'] = year
        return self

    def track_num(self, track_num):
        '''Track number of the current track. Represents the current position of the track in the album.'''
        if not isinstance(track_num, int):
            raise TypeError("track number must be expressed as an integer.")
        
        self._params['track_num'] = track_num
        return self

    def cover(self, cover):
        '''Cover art url.'''
        self._params['cover'] = cover
        return self

    def build(self):
        '''Build a Song using all the params provided.'''
        if not self._params.get('title') or not self._params.get('album') or not self._params.get('artist'):
            raise ValueError("The following are mandatory: title, album, artist.")

        return Song(**self._params)

class ResponseBody:
    '''
        Model-Object to represent a response, hold data from response, and manage exceptions for the app.
    '''
    def __init__(self, **kwargs):
        self.url: str = kwargs.get('url', "")
        self.response_code: int = kwargs.get('response_code', 0)
        self.response:  requests.Response = kwargs.get('response', None)
        self.response_json: dict = kwargs.get('response_json', {})
        self.result_list: list = kwargs.get('result_list', [])
        self.errs: deque = kwargs.get('errs', deque())
        self.is_success: bool = kwargs.get('is_success', False)
        self.debug: bool= kwargs.get('debug', __debugflg__())

    def get(self):
        '''
            Perform a get request on the endpoint url.

            Throws:
                * OdnoException if an exception is encountered.
        '''
        try:
            if self.url == "" or not isinstance(self.url, str):
                raise ValueError("ERROR:Invalid URL.")

            resp:requests.Response = requests.get(self.url, timeout=20)

            self.response_code = resp.status_code

            if resp.ok:
                self.response = resp
                self.is_success = True

            if not resp.ok:
                self.is_success = False
                resp.raise_for_status()

            if b'xml' not in resp.content:
                self.response_json = resp.json()
                self.is_success = True

            return self

        except (TypeError, ValueError, requests.exceptions.HTTPError) as e:
            odno_exception:OdnoException = None

            if isinstance(e,TypeError):
                odno_exception = OdnoException("TypeError: An error ocurred capturing resp.content.", e)

            elif isinstance(e, ValueError):
                odno_exception = OdnoException("ValueError: Invalid URL", e)

            else:
                odno_exception = OdnoException(f"HTTPError: GET request to {self.url} could not be completed...", e)

            OdnoException.handle_exception(odno_exception, odno_exception.message, "ResponseBody.get")
            self.errs.appendleft(odno_exception.message)
            self.is_success = False
            return self

    def show_errors(self):
        '''log exceptions if any'''
        if __debugflg__():
            errors = self.errs.copy()
            odnologger.log(log_level="ERROR", msg="The following error(s) ocurred:")
            while errors:
                odnologger.log(log_level="ERROR", msg=f"error:{self.errs.pop()}")
            del errors

    def reset(self) -> None:
        '''reset response'''
        self.response_code = 0
        self.response = None
        self.response_json = {}
        self.result_list = []
        self.is_success = False
        if self.errs:
            odnologger.log(log_level="WARN", msg="The following exceptions were captured:\n")
            odnologger.log(log_level="WARN", msg=str(self.errs), module_name='ResponseBody.reset')
        self.errs = []
        self.url = ""

    def __str__(self):
        return f"response body: [response_code={self.response_code}, response={self.response}, debug={self.debug}]"

    def __repr__(self):
        return self.__str__()

class ResponseBodyBuilder:
    '''
        ResponseBody Builder.
        Returns a ResponseBody when build is invoked.
    '''
    def __init__(self):
        self._params = {}

    def url(self, url):
        '''URL used or get requests'''
        self._params['url'] = url
        return self

    def response_code(self, response_code):
        '''Response Code of the http request.'''
        self._params['response_code'] = response_code
        return self

    def response(self, response):
        '''response from the http request'''
        self._params['response'] = response
        return self

    def response_json(self, response_json):
        '''JSON response from the http request'''
        self._params['response_json'] = response_json
        return self

    def result_list(self, result_list):
        '''result list'''
        self._params['result_list'] = result_list
        return self

    def errs(self, err_msgs:str):
        '''Store exception err messages if any have occurred'''

        err_stack:deque = self._params['errs']
        err_stack.appendleft(err_msgs)
        return self

    def is_success(self, is_success):
        '''Set success flag'''
        self._params['is_success'] = is_success
        return self

    def debug(self, debug):
        '''Set debug flag'''
        self._params['debug'] = debug
        return self

    def build(self):
        '''Build ResponseBody'''
        return ResponseBody(**self._params)
