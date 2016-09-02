# -*- coding: utf-8 -*-
"""
西部信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy

from bs4 import BeautifulSoup as bs
import re
import hashlib

from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime


class TrustWtixaSpider(scrapy.Spider):
    name = "trust10_spider"
    allowed_domains = ["wti-xa.com"]
    start_urls = [
        "http://www.wti-xa.com/gongsixinwen_single_jingzhi.jsp",
    ]

    def parse(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 7 or tds[0].text == '产品名称':
                continue

            item = FundSpiderItem()
            item['fund_name'] = tds[0].text.strip()
            item['fund_full_name'] = item['fund_name']
            # item['open_date'] = tds[2].text.strip()
            item['nav'] = tds[2].text.strip()
            if tds[3].text.strip() != '-':
                item['added_nav'] = tds[3].text.strip()
            item['foundation_date'] = tds[6].text.strip()
            item['statistic_date'] = tds[5].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = 'TG0010'

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item['uuid'], item['fund_name'], item['statistic_date']
            yield item

            # 历史净值
            href = tds[0].find('a')['href']
            if 'http' not in href:
                href = "http://www.wti-xa.com/" + href
            yield scrapy.Request(href, callback=lambda response, item=item: self.parse_history_nav(response, item))


    # def parse_history_link(self, response, item):
    #     self.log(response.url)
    #
    #     soup = bs(response.body, 'lxml')
    #     pages = soup.find('div', {'class':'pages'})
    #     if pages:
    #         hrefs = pages.find_all('a')
    #         for a in hrefs:
    #             href = a['href']
    #             if 'http' not in href:
    #                 href = "http://www.siti.com.cn/" + href
    #             yield scrapy.Request(href,
    #                                  callback=lambda response, item=item: self.parse_history_nav(response, item))


    def parse_history_nav(self, response, itemTop):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 5 or tds[0].text.strip() == '日期':
                continue

            item = FundSpiderItem()
            # item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = itemTop['fund_name']
            # item['open_date'] = itemTop['open_date']
            item['nav'] = tds[1].text.strip()
            if tds[2].text.strip() != '-':
                item['added_nav'] = tds[2].text.strip()
            item['foundation_date'] = itemTop['foundation_date']
            item['statistic_date'] = tds[0].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = response.url
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item['fund_name'], item['statistic_date']
            yield item