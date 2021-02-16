# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy_splash import SplashCookiesMiddleware
import logging


logger = logging.getLogger(__name__)


class YtcCookiesMiddleware(SplashCookiesMiddleware):

    def process_response(self,request,response,spider):
        response = super(YtcCookiesMiddleware,self).process_response(request,response,spider)
        splash_options = request.meta['splash']
        session_id = splash_options.get('new_session_id',splash_options.get('session_id'))
        if session_id is None:
            return response
        jar = self.jars[session_id]
        try:
            jar.clear('.www.youtube.com','/','requests')
        except KeyError as error:
            msg = 'Request Cookie not present'
            logger.debug(msg, extra={'spider': spider})
        response.cookiejar = jar
        return response


class YtcDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
