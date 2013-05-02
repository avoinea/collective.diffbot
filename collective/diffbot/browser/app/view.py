""" View
"""
import logging
import urllib2
from urllib import urlencode
from zope.component import queryUtility
import json as simplejson
from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from collective.diffbot.interfaces import IDiffbotSettings
from collective.diffbot.cache import ramcache, cacheJsonKey

logger = logging.getLogger('collective.diffbot')

class Diffbot(BrowserView):
    """ Diffbot
    """
    def __init__(self, context, request):
        super(Diffbot, self).__init__(context, request)
        self._settings = None

    @property
    def headers(self):
        """ Headers
        """
        return {
            'User-Agent' : 'collective.diffbot'
        }

    @property
    def settings(self):
        """ Settings
        """
        if self._settings is None:
            self._settings = queryUtility(
                IRegistry).forInterface(IDiffbotSettings, False)
        return self._settings

    @ramcache(cacheJsonKey, dependencies=['collective.diffbot'])
    def _json(self, **kwargs):
        """ Get JSON from diffbot
        """
        res = simplejson.dumps({})
        url = self.request.form.get('url', None)
        if not url:
            logger.warn("Invalid url provided %s", url)
            return res

        diffbot = self.settings.url
        token = self.settings.token

        query = urlencode(dict(token=token, url=url))
        try:
            #request = urllib2.Request(diffbot, query, headers=self.headers)
            conn = urllib2.urlopen(diffbot + "?" + query)
        except Exception, err:
            logger.exception(err)
        else:
            res = conn.read()
        finally:
            conn.close()
        return res

    def json(self, **kwargs):
        """ Get JSON from diffbot
        """
        self.request.response.setHeader('content-type', 'application/json')
        json = self._json(**kwargs)
        callback = self.request.get('callback', None)
        if not callback:
            return json

        # JSONP
        if isinstance(callback, str):
            callback = callback.decode('utf-8')
        if isinstance(json, str):
            json = json.decode('utf-8')
        return callback + u'(' + json + u')'
