#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
from requests.cookies import RequestsCookieJar
from json import dumps

from django.conf import settings

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/4.0(compatible; ExProxy/0.1; +https://github.com/jackyyf/exshare)'
_init = False

def init():
    try:
        # First try to login using username/password pair
        username = settings.EXHENTAI_USER
        password = settings.EXHENTAI_PASS
        # Do login job here.
        post_data = {
            'referer' : 'https://forums.e-hentai.org/index.php',
            'UserName' : username,
            'PassWord' : password,
            'CookieDate' : '1',
        }
        resp = session.post('https://forums.e-hentai.org/index.php?act=Login&CODE=01', post_data)
        if resp.status_code > 299:
            raise RuntimeError('Server responsed while login, with code %d' % resp.status_code)
        data = resp.text
        if 'Username or password incorrect' in data:
            raise RuntimeError('Invalid password')
        if 'You must already have registered for an account before you can log in' in data:
            raise RuntimeError('No such username')
        if 'You are now logged in as:' not in data:
            raise RuntimeError('Unknown response while login.')
        eh_cookie = session.cookies.get_dict()
        for k, v in eh_cookie.iteritems():
            session.cookies.set(k, v, domain='.exhentai.org', path='/')
    except AttributeError:
        # Cookie provided?
        try:
            cookie = settings.EXHENTAI_COOKIE
            session.cookies = RequestsCookieJar()
            if isinstance(cookie, dict):
                for k, v in cookie.iteritems():
                    session.cookies.set(k, v, domain='.e-hentai.org', path='/')
                    session.cookies.set(k, v, domain='.exhentai.org', path='/')
            elif isinstance(cookie, list):
                for item in cookie:
                    try:
                        k, v = item.split('=', 1)
                    except ValueError:
                        raise ValueError('Invalid cookie string: %s' % item)
                    session.cookies.set(k, v, domain='.e-hentai.org', path='/')
                    session.cookies.set(k, v, domain='.exhentai.org', path='/')
            elif isinstance(cookie, basestring):
                # ';' separated cookie string
                cookies = filter(None, map(lambda s : s.strip(), cookie.split(';')))
                for item in cookies:
                    try:
                        k, v = item.split('=', 1)
                    except ValueError:
                        raise ValueError('Invalid cookie string: %s' % item)
                    session.cookies.set(k, v, domain='.e-hentai.org', path='/')
                    session.cookies.set(k, v, domain='.exhentai.org', path='/')
            # Now let's check if cookie works.
            resp = session.get('http://exhentai.org')
            if resp.headers['Content-Type'] == 'image/gif':
                raise ValueError('Unable to login by cookie: sad panda >^<')
        except AttributeError:
            raise ValueError('No exhentai user/pass pair or cookie provided!')

def get_meta(gid, token):
    if not _init:
        init()
    # Change to g.e-hentai.org if you need to.
    json_data = {
        "method": "gdata",
        "namespace": "1",
        "gidlist": [
            [gid, token]
        ]
    }
    resp = session.post('http://exhentai.org/api.php', json=json_data)
    if resp.status_code > 299:
        raise ValueError('Invalid response code: %d' % resp.status_code)
    try:
        data = resp.json()
    except ValueError as e:
        raise RuntimeError(e)
    if u'error' in data:
        raise ValueError('Invalid gid or token.')
    assert 'gmetadata' in data and isinstance(data['gmetadata'], list)
    return data['gmetadata'][0]