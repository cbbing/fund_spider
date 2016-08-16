# -*- coding: utf-8 -*-
"""
中融信托
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


class TrustZritcSpider(scrapy.Spider):
    name = "trust_zritc_spider"
    allowed_domains = ["zritc.com"]
    start_urls = ["http://www.zritc.com/InformationDisclosure/Index?pageIndex={}".format(i) for i in range(1, 17241)]

    def parse(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 4 or tds[0].text == '名称':
                continue

            item = FundSpiderItem()
            item['fund_name'] = tds[0].text.strip()
            item['nav'] = tds[1].text.strip()
            item['added_nav'] = tds[2].text.strip()
            item['statistic_date'] = tds[3].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = 'TG0003'

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item['uuid'], item['fund_name'], item['statistic_date']
            yield item


