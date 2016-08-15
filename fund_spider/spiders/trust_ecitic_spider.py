# -*- coding: utf-8 -*-
"""
中信信托
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


class TrustEciticSpider(scrapy.Spider):
    name = "trust_ecitic_spider"
    # allowed_domains = ["trust.ecitic.com"]
    start_urls = (
        'http://trust.ecitic.com/XXPL_JZPL/index.jsp?type=1',
    )


    def parse(self, response):
        """
        中信信托
        :param response:
        :return:
        """
        self.log(response.url)
        # print response.url

        # 请求第一页
        yield scrapy.Request(response.url, callback=self.parse_item)

        # 请求其它页
        for page in response.xpath('//div[@class="pagebar"]/a'):
            link = page.xpath('@href').extract()[0]
            if 'http' not in link:
                link = "http://trust.ecitic.com/XXPL_JZPL/" + link

            self.log(link)
            print link
            yield scrapy.Request(link, callback=self.parse_item)


    def parse_item(self, response):
        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 8 or tds[0].text == '序号':
                continue

            item = FundSpiderItem()
            # item['fund_id'] = ''
            item['fund_name'] = tds[1].text.strip()
            item['fund_full_name'] = "中信信托." + item['fund_name'] + "证券投资集合资金信托"
            item['open_date'] = tds[2].text.strip()
            item['nav'] = tds[3].text.strip()
            item['added_nav'] = tds[4].text.strip()
            item['foundation_date'] = tds[6].text.strip()
            item['statistic_date'] = tds[7].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = 'TG0001'



            item['uuid'] = hashlib.md5((item['fund_name']+item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item

            # 产品详情
            href = tds[1].find('a')['href']
            if 'http' not in href:
                href = "http://trust.ecitic.com/XXPL_JZPL/" + href
            yield scrapy.Request(href, callback=lambda response, itemTop=item : self.parse_detail(response, itemTop))





    def parse_detail(self, response, itemTop):
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('ul')
        for tr in trs:
            tds = tr.find_all('li')
            if len(tds) != 4 or tds[0].text == '估值基准日':
                continue

            item = FundSpiderItem()
            # item['fund_id'] = ''
            item['fund_name'] = itemTop['fund_name']
            item['fund_full_name'] = "中信信托." + item['fund_name'] + "证券投资集合资金信托"
            item['open_date'] = itemTop['open_date']
            item['nav'] = tds[1].text.strip()
            # item['added_nav'] =
            item['foundation_date'] = itemTop['foundation_date']
            item['statistic_date'] = tds[0].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = response.url
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item


