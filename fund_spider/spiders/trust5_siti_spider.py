# -*- coding: utf-8 -*-
"""
陕国投
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


class TrustSitiSpider(scrapy.Spider):
    name = "trust_siti_spider"
    allowed_domains = ["siti.com.cn"]
    start_urls = ["http://www.siti.com.cn/product.php?fid=23&fup=3&pageid={}".format(i) for i in range(1, 7)]

    def parse(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 10 or tds[0].text == '序号':
                continue

            item = FundSpiderItem()
            item['fund_name'] = tds[1].text.strip()
            item['open_date'] = tds[2].text.strip()
            item['nav'] = tds[4].text.strip()
            item['added_nav'] = tds[5].text.strip()
            item['foundation_date'] = tds[8].text.strip()
            item['statistic_date'] = tds[9].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = 'response.url'
            item['org_id'] = 'TG0005'

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            # print item['uuid'], item['fund_name'], item['statistic_date']
            yield item

            # 历史净值
            href = tds[1].find('a')['href']
            if 'http' not in href:
                href = "http://www.siti.com.cn/" + href
            yield scrapy.Request(href, callback=lambda response, item=item: self.parse_history_link(response, item))


    def parse_history_link(self, response, item):
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        pages = soup.find('div', {'class':'pages'})
        if pages:
            hrefs = pages.find_all('a')
            for a in hrefs:
                href = a['href']
                if 'http' not in href:
                    href = "http://www.siti.com.cn/" + href
                yield scrapy.Request(href,
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
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 6 or '年' not in tds[0].text.strip() :
                continue

            item = FundSpiderItem()
            # item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = itemTop['fund_name']
            item['open_date'] = itemTop['open_date']
            item['nav'] = tds[2].text.strip()
            item['added_nav'] = tds[3].text.strip()
            item['foundation_date'] = itemTop['foundation_date']
            item['statistic_date'] = tds[0].text.strip().replace('年','-').replace('月','-').replace('日','')

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = response.url
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            # print item['fund_name'], item['statistic_date']
            yield item