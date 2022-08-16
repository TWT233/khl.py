"""khl raw API and related helpers"""
# pylint: skip-file
# this file contains hax to generate/interpolate stub code which make pylint pains
import functools
import inspect
import logging
import re
from collections import namedtuple
from typing import Callable, Tuple

import aiohttp

log = logging.getLogger(__name__)

_RE_ROUTE = re.compile(r'(?<!^)(?=[A-Z])')

_Req = namedtuple('_Req', ['method', 'route', 'params'])


def req(method: str, **http_fields):
    """meta-decorator

    :returns a decorator to fill func with boilerplate"""

    def _method(func: Callable):

        @functools.wraps(func)
        def req_maker(*args, **kwargs) -> _Req:
            route = _RE_ROUTE.sub('-', func.__qualname__).lower().replace('.', '/')

            # dump args into kwargs
            param_names = list(inspect.signature(func).parameters.keys())
            for i, arg in enumerate(args):
                kwargs[param_names[i]] = arg

            params = _merge_params(method, http_fields, kwargs)
            return _Req(method, route, params)

        return req_maker

    return _method


def _merge_params(method: str, http_fields: dict, req_args: dict) -> dict:
    payload = req_args
    payload_key = 'params'  # default payload_key: params=
    if method == 'POST':
        payload_key = 'json'  # POST: in default json=

        content_type = http_fields.get('headers', {}).get('Content-Type', None)
        if content_type == 'multipart/form-data':
            payload_key, payload = _build_form_payload(req_args)
            # headers of form-data req are delegated to aiohttp
            http_fields = _remove_content_type(http_fields)
        elif content_type is not None:
            raise ValueError(f'unrecognized Content-Type {content_type}')

    params = {payload_key: payload}
    params.update(http_fields)
    return params


def _remove_content_type(http_fields: dict) -> dict:
    """in some situation, such as content-type=multipart/form-data,
    content-type should be delegated to aiohttp to auto-generate,
    thus content-type is required to be removed in http_fields
    """
    if http_fields.get('headers', {}).get('Content-Type', None) is not None:
        http_fields = http_fields.copy()
        http_fields['headers'] = http_fields.get('headers', {}).copy()
        del http_fields['headers']['Content-Type']
    return http_fields


def _build_form_payload(req_args: dict) -> Tuple[str, aiohttp.FormData]:
    data = aiohttp.FormData()
    for name, value in req_args.items():
        data.add_field(name, value)
    return 'data', data


class Guild:
    """mapped to route: /guild/*"""

    @staticmethod
    @req('GET')
    def list():
        ...

    @staticmethod
    @req('GET')
    def view(guild_id):
        ...

    @staticmethod
    @req('GET')
    def userList(
        guild_id,
        channel_id=None,
        search=None,
        role_id=None,
        mobile_verified=None,
        active_time=None,
        joined_at=None,
        page=None,
        page_size=None,
    ):
        ...

    @staticmethod
    @req('POST')
    def nickname(
        guild_id,
        nickname,
        user_id,
    ):
        ...

    @staticmethod
    @req('POST')
    def leave(guild_id):
        ...

    @staticmethod
    @req('POST')
    def kickout(guild_id, target_id):
        ...


class GuildMute:

    @staticmethod
    @req('GET')
    def list(guild_id, return_type):
        ...

    @staticmethod
    @req('POST')
    def create(
        guild_id,
        user_id,
        type,
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(
        guild_id,
        user_id,
        type,
    ):
        ...


class Blacklist:

    @staticmethod
    @req('GET')
    def list(
            guild_id
    ):
        ...

    @staticmethod
    @req('POST')
    def create(
            guild_id,
            target_id,
            remark,
            del_msg_days
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(
            guild_id,
            target_id
    ):
        ...


class Badge:

    @staticmethod
    @req('GET')
    def guild(
            guild_id,
            style
    ):
        ...


class Channel:

    @staticmethod
    @req('GET')
    def list(guild_id):
        ...

    @staticmethod
    @req('GET')
    def view(target_id):
        ...

    @staticmethod
    @req('POST')
    def create(guild_id, parent_id, name, type, limit_amount, voice_quality, is_category):
        ...

    @staticmethod
    @req('POST')
    def delete(channel_id):
        ...

    @staticmethod
    @req('POST')
    def moveUser(target_id, user_ids):
        ...

    @staticmethod
    @req('POST')
    def update(channel_id, name, topic, slow_mode):
        ...


class ChannelRole:

    @staticmethod
    @req('GET')
    def index(channel_id):
        ...

    @staticmethod
    @req('POST')
    def create(
        channel_id,
        type,
        value,
    ):
        ...

    @staticmethod
    @req('POST')
    def update(
        channel_id,
        type,
        value,
        allow,
        deny,
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(
        channel_id,
        type,
        value,
    ):
        ...


class ChannelUser:

    @staticmethod
    @req('GET')
    def getJoinedChannel(page, page_size, guild_id, user_id):
        ...


class Message:

    @staticmethod
    @req('GET')
    def view(msg_id):
        ...

    @staticmethod
    @req('GET')
    def list(
        target_id,
        msg_id,
        pin,
        flag,
    ):
        ...

    @staticmethod
    @req('POST')
    def create(
        type,
        target_id,
        content,
        quote,
        nonce,
        temp_target_id,
    ):
        ...

    @staticmethod
    @req('POST')
    def update(
        msg_id,
        content,
        quote,
        temp_target_id,
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(msg_id, ):
        ...

    @staticmethod
    @req('GET')
    def reactionList(msg_id, emoji):
        ...

    @staticmethod
    @req('POST')
    def addReaction(msg_id, emoji):
        ...

    @staticmethod
    @req('POST')
    def deleteReaction(msg_id, emoji, user_id):
        ...

    @staticmethod
    @req('POST')
    def addReaction(msg_id, emoji):
        ...

    @staticmethod
    @req('POST')
    def addReaction(msg_id, emoji):
        ...


class UserChat:

    @staticmethod
    @req('GET')
    def list():
        ...

    @staticmethod
    @req('GET')
    def view(chat_code):
        ...

    @staticmethod
    @req('POST')
    def create(target_id):
        ...

    @staticmethod
    @req('POST')
    def delete(chat_code):
        ...


class DirectMessage:

    @staticmethod
    @req('GET')
    def list(
        chat_code,
        target_id,
        msg_id,
        flag,
    ):
        ...

    @staticmethod
    @req('POST')
    def create(
        type,
        target_id,
        chat_code,
        content,
        quote,
        nonce,
    ):
        ...

    @staticmethod
    @req('POST')
    def update(
        msg_id,
        content,
        quote,
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(msg_id):
        ...

    @staticmethod
    @req('GET')
    def reactionList(msg_id, emoji):
        ...

    @staticmethod
    @req('POST')
    def addReaction(msg_id, emoji):
        ...

    @staticmethod
    @req('POST')
    def deleteReaction(msg_id, emoji, user_id):
        ...


class Gateway:

    @staticmethod
    @req('GET')
    def index(compress):
        ...


class User:

    @staticmethod
    @req('GET')
    def me():
        ...

    @staticmethod
    @req('GET')
    def view(
        user_id,
        guild_id=None,
    ):
        ...

    @staticmethod
    @req('POST')
    def offline(
    ):
        ...


class Asset:

    @staticmethod
    @req('POST', headers={'Content-Type': 'multipart/form-data'})
    def create(file):
        ...


class GuildRole:

    @staticmethod
    @req('GET')
    def list(guild_id):
        ...

    @staticmethod
    @req('POST')
    def create(
        name,
        guild_id,
    ):
        ...

    @staticmethod
    @req('POST')
    def update(
        guild_id,
        role_id,
        hoist,
        mentionable,
        permissions,
        color,
        name,
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(
        guild_id,
        role_id,
    ):
        ...

    @staticmethod
    @req('POST')
    def grant(
        guild_id,
        user_id,
        role_id,
    ):
        ...

    @staticmethod
    @req('POST')
    def revoke(
        guild_id,
        user_id,
        role_id,
    ):
        ...


class Intimacy:

    @staticmethod
    @req('GET')
    def index(user_id):
        ...

    @staticmethod
    @req('POST')
    def update(
        user_id,
        score,
        social_info,
        img_id,
    ):
        ...


class GuildEmoji:

    @staticmethod
    @req('GET')
    def list(guild_id):
        ...

    @staticmethod
    @req('POST', headers={'Content-Type': 'multipart/form-data'})
    def create(
        name,
        guild_id,
        emoji,
    ):
        ...

    @staticmethod
    @req('POST')
    def update(
        name,
        id,
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(id):
        ...


class Invite:

    @staticmethod
    @req('GET')
    def list(
        guild_id,
        channel_id,
        page,
        page_size
    ):
        ...

    @staticmethod
    @req('POST')
    def create(
        guild_id,
        channel_id,
        duration,
        setting_times
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(
        url_code,
        guild_id,
        channel_id
    ):
        ...


@req('GET')
def game():
    ...


class Game:

    @staticmethod
    @req('POST')
    def create(
        name,
        process_name,
        icon,
    ):
        ...

    @staticmethod
    @req('POST')
    def update(
        id,
        name,
        icon,
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(id):
        ...

    @staticmethod
    @req('POST')
    def activity(data_type, id=None, music_name=None, singer=None, software=None):
        ...

    @staticmethod
    @req('POST')
    def deleteActivity(data_type):
        ...


class Oauth2:

    @staticmethod
    @req("POST")
    def token(
        grant_type,
        client_id,
        client_secret,
        code,
        redirect_uri
    ):
        ...
