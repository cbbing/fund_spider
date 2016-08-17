# -*- coding: utf-8 -*-
"""
云南信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy

from bs4 import BeautifulSoup as bs
import re
import hashlib

from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime


class TrustYnTrustSpider(scrapy.Spider):
    name = "trust8_yntrust_spider"
    allowed_domains = ["yntrust.com"]
    start_urls = ["http://www.yntrust.com/index!netValue.xhtml?pager.offset=0&id="]

    def parse(self, response):
        self.log(response.url)

        # 第一页
        yield scrapy.Request(response.url, callback=self.parse_item)

        # 翻页
        urls = response.xpath('//a[contains(@href, "/index!netValue.xhtml?pager.offset")]/@href').extract()
        for url in urls:
            if 'http' not in url:
                url = "http://www.yntrust.com" + url
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        self.log(response.url)
        soup = bs(response.body, 'lxml')
        trs = soup.find_all('dd')
        for tr in trs:

            item = FundSpiderItem()

            a = tr.find('a', href=re.compile(r"/netValueView/.*"), text=re.compile(".+"))
            if not a:
                continue
            item['fund_name'] = a.text.strip()

            h2s = tr.find_all('h2')
            if len(h2s) == 2:
                item['nav'] = h2s[0].text.strip()
                item['foundation_date'] = h2s[1].text.strip()
            else:
                continue

            # item['added_nav'] = tds[5].text.strip()
            # item['foundation_date'] = tds[8].text.strip()
            # item['statistic_date'] = tds[9].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = 'TG0008'

            # item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            # print item

            # 历史净值
            href = a['href']
            if 'http' not in href:
                href = "http://www.yntrust.com/" + href
            yield scrapy.Request(href, callback=lambda response, item=item: self.parse_history_link(response, item))

    def parse_history_link(self, response, item):
        self.log(response.url)

        # 翻页
        urls = response.xpath('//a[contains(@href, "/index!netValueView.xhtml?pager.offset=")]/@href').extract()
        for url in urls:
            url = url if 'http' in url else "http://www.yntrust.com" + url
            yield scrapy.Request(url,
                                 callback=lambda response, item=item: self.parse_history_nav(response, item))

    def parse_history_nav(self, response, itemTop):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        article = soup.find('div', {'class':'article'})
        if not article:
            return
        trs = article.find_all('dd')
        for tr in trs:

            item = FundSpiderItem()

            item['statistic_date'] = tr.find('span').text.strip()
            item['nav'] = tr.find('p').text.strip()
            item['added_nav'] = tr.find('b').text.strip()

            # item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = itemTop['fund_name']
            # item['open_date'] = itemTop['open_date']
            item['foundation_date'] = itemTop['foundation_date']

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = response.url
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item