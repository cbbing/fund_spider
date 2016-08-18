# -*- coding: utf-8 -*-

from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse, Response

import fund_spider.middlewares.downloader as downloader

class CustomMiddlewares(object):
    def process_request(self, request, spider):
        url = str(request.url)
        dl = downloader.CustomDownloader()
        content = dl.get_page_source(url)
        return HtmlResponse(url, status = 200, body = content, encoding='utf-8')

    def process_response(self, request, response, spider):
        if len(response.body) == 100:
            return IgnoreRequest("body length == 100")
        else:
            return response