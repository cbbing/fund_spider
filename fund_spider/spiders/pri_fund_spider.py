# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from bs4 import BeautifulSoup as bs
import re
import hashlib

from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime


class PriFundSpiderSpider(CrawlSpider):
    name = "pri_fund_spider"
    allowed_domains = ["http://trust.ecitic.com/"]
    start_urls = (
        'http://trust.ecitic.com/XXPL_JZPL/index.jsp?type=1',
    )

    rules = (
        Rule(LinkExtractor(allow=(r'http://trust.ecitic.com/XXPL_JZPL/index.jsp')), callback='parse'),
    )

    def parse(self, response):
        """
        中信信托
        :param response:
        :return:
        """
        print "parse url:%s" % response.url

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 8 or tds[0].text == '序号':
                continue

            item = FundSpiderItem()
            item['fund_id'] = ''
            item['fund_name'] = tds[1].text.strip()
            item['fund_full_name'] = "中信信托." + item['fund_name'] + "证券投资集合资金信托"
            item['open_date'] = tds[2].text.strip()
            item['nav'] = tds[3].text.strip()
            item['added_nav'] = tds[4].text.strip()
            item['foundation_date'] = tds[6].text.strip()
            item['statistic_date'] = tds[7].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = 'http://trust.ecitic.com/XXPL_JZPL/index.jsp?type=1'
            item['org_id'] = 'TG0001'

            item['uuid'] = hashlib.md5(item['fund_name'].encode('utf8')).hexdigest()
            print item
            yield item





