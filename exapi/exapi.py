#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import urllib

import requests
from requests.cookies import RequestsCookieJar
from pyquery import PyQuery as PQ
import logging

logger = logging.getLogger('exapi.exapi')

from django.conf import settings

class ExHentaiSession(requests.Session):

    def __init__(self):
        super(ExHentaiSession, self).__init__()
        self.logger = logging.getLogger('exapi.http')

    def get(self, url, **kwargs):
        try:
            resp = super(ExHentaiSession, self).get(url, **kwargs)
            if resp.status_code < 400:
                self.logger.info('GET %s => %d' % (url, resp.status_code))
            else:
                self.logger.warn('GET %s => %d' % (url, resp.status_code))
            return resp
        except Exception as e:
            self.logger.exception('GET %s: ', e)
            raise

    def post(self, url, data=None, json=None, **kwargs):
        try:
            resp = super(ExHentaiSession, self).post(url, data=data, json=json, **kwargs)
            if resp.status_code < 400:
                self.logger.info('POST %s => %d' % (url, resp.status_code))
            else:
                self.logger.warn('POST %s => %d' % (url, resp.status_code))
            return resp
        except Exception as e:
            self.logger.exception('POST %s: ', e)
            raise

session = ExHentaiSession()
session.headers['User-Agent'] = 'Mozilla/4.0(compatible; ExProxy/0.1; +https://github.com/jackyyf/exshare)'
_init = False

def init():
    if _init:
        return
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

if settings.EXHENTAI_VALIDATE_ON_START:
    init()

def get_meta(gid, token):
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
    assert 'gmetadata' in data and isinstance(data['gmetadata'], list)
    ret = data['gmetadata'][0]
    if 'error' in ret:
        raise ValueError('Invalid gid or token: %s' % ret['error'])
    return ret

def fetch_meta(glist):
    # GList should be a list, and each element should be a two element tuple/list, in form (gid, token)
    # Do a little validate job.
    payload = []
    for gid, token in glist:
        gid = int(gid)
        payload.append((gid, token))
    json_data = {
        'method': 'gdata',
        'namespace': '1',
        'gidlist': payload,
    }
    resp = session.post('http://exhentai.org/api.php', json=json_data)
    if resp.status_code > 299:
        raise ValueError('Invalid response code: %d' % resp.status_code)
    try:
        data = resp.json()
    except ValueError as e:
        raise RuntimeError(e)
    assert 'gmetadata' in data and isinstance(data['gmetadata'], list)
    # You should check for error your self, since request are likely to be partial succeeded.
    return data['gmetadata']

def fetch_page(page=None):
    # NOTE: page argument start with index 0, although they display as 1.
    init()
    url = 'http://exhentai.org/'
    if page is not None:
        url += '?page=' + urllib.quote(str(page))
    resp = session.get(url)
    if resp.status_code > 299:
        logger.warn('Server responded with status code %d' % resp.status_code)
        return []
    pq = PQ(resp.text)
    rows = pq('div.ido table.itg tr').items()
    ret = []
    for row in rows:
        if not row.attr('class'):
            continue
        for link in row('a'):
            href = link.attrib.get('href', '')
            if href.startswith('http://exhentai.org/g/'):
                logger.debug('Found a possible link: %s' % href)
                href = href[len('http://exhentai.org/g/') : ].rstrip('/')
                try:
                    gid, gtoken = href.split('/', 1)
                    gid = int(gid)
                except ValueError as e:
                    logger.error('Error parsing link, ignored.')
                    continue
                logger.debug('Gallery parsed successfully: gid=%d token="%s"' % (gid, gtoken))
                ret.append((gid, gtoken))
    logger.info('Found %d galleries.' % len(ret))
    return ret
