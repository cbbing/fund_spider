# -*- coding: utf-8 -*-
"""
西藏信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy

from bs4 import BeautifulSoup as bs
import re
import hashlib
import json
from scrapy.http import FormRequest

from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime


class TrustTtcopider(scrapy.Spider):
    name = "trust9_ttco_spider"
    allowed_domains = ["ttco.cn"]

    start_urls = (
        'http://www.ttco.cn/ttco/page_networth',
    )

    # def start_requests(self):
    #     url = "http://www.fotic.com.cn/DesktopModules/ProductJZ/GetJsonResult.ashx"
    #     requests = []
    #     formdata = {"programName": "",
    #                 "sDate": "",
    #                 "eDate": "",
    #                 "pageNo": "1",
    #                 "pageSize": "10"
    #                 }
    #
    #     request = FormRequest(url, callback=self.parse, formdata=formdata)
    #     requests.append(request)
    #     return requests


    def parse(self, response):
        self.log(response.url)

        # 请求第一页
        yield scrapy.Request(response.url, callback=self.parse_item)

        # 请求其它页
        soup = bs(response.body, 'lxml')
        pageSum = soup.find('font', {'id':'_pageSum'})
        if pageSum:
            page_sum = int(pageSum.text)
            for i in range(2, page_sum+1):
                formdata = {"st": "dd",
                            "netWorthPage.pageSize": "10",
                            "netWorthPage.pageNum": str(i),
                            }
                yield FormRequest(response.url, callback=self.parse_item, formdata=formdata, dont_filter=True)


    def parse_item(self, response):
        self.log(response.url)
        # print response.url

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 8 or tds[0].text == '产品名称':
                continue

            item = FundSpiderItem()

            item['fund_name'] = tds[0].text.strip()
            # item['open_date'] = tds[2].text.strip()
            item['nav'] = tds[3].text.strip()
            item['added_nav'] = tds[4].text.strip()
            # item['foundation_date'] = tds[8].text.strip()
            item['statistic_date'] = tds[7].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = 'TG0005'

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            # yield item

            # 历史净值
            href = tds[0].find('a')['href']
            if 'http' not in href:
                href = "http://www.ttco.cn" + href
            yield scrapy.Request(href, callback=lambda response, item=item: self.parse_history_link(response, item))

    def parse_history_link(self, response, item):
        self.log(response.url)

        # 获取当前页的历史净值
        yield scrapy.Request(response.url,
                             callback=lambda response, item=item: self.parse_history_nav(response, item))

        # 翻页
        urls = response.xpath('//a[contains(@href, "http://www.ttco.cn/ttco/networthList?netWorthNetPage.start=")]/@href').extract()
        for url in urls:
            url = url if 'http' in url else "http://www.ttco.cn" + url
            yield scrapy.Request(url,
                                 callback=lambda response, item=item: self.parse_history_link(response, item))

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
            if len(tds) != 4 or tds[0].text == '日期':
                continue

            item = FundSpiderItem()
            # item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = itemTop['fund_name']
            item['nav'] = tds[1].text.strip()
            item['added_nav'] = tds[2].text.strip()
            item['statistic_date'] = tds[0].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = response.url
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item['fund_name'], item['statistic_date']
            yield item





