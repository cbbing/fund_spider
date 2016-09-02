# -*- coding: utf-8 -*-
"""
兴业信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from bs4 import BeautifulSoup as bs
import re
import hashlib
import json
from selenium import webdriver
import time

import scrapy
from scrapy.http import FormRequest, HtmlResponse

from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime


class TrustMinTrustSpider(scrapy.Spider):
    name = "trust12_spider"
    allowed_domains = ["ciit.com.cn"]

    start_urls = (
        'http://www.ciit.com.cn/xingyetrust-web/netvalues/netvalue!getValue?type=1',
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
        yield scrapy.Request(response.url, callback=self.parse_item, dont_filter=True)

        # 请求其它页
        soup = bs(response.body, 'lxml')
        pageSum = soup.find('a', text='尾页')
        if pageSum:
            findPage = re.search('\d+', pageSum['href'])
            if findPage:
                page_sum = int(findPage.group())
                for i in range(2, page_sum+1):
                    url = response.url + "&currentpage=" + str(i)
                    yield scrapy.Request(url, callback=self.parse_item)


    def parse_item(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 6 or tds[0].text == '序号':
                continue

            item = FundSpiderItem()

            item['fund_name'] = tds[1].text.strip()
            item['fund_full_name'] = item['fund_name']
            # item['open_date'] = tds[2].text.strip()
            item['nav'] = tds[3].text.strip()
            # item['added_nav'] = tds[2].text.strip()
            item['foundation_date'] = tds[2].text.strip()
            item['statistic_date'] = tds[4].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = 'TG0012'

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()

            # http: // www.ttco.cn / ttco / product_detail_founded?product.id = AF8A170DAC444375A47F368F28F83254
            href = tds[1].find('a')['href']
            findProId = re.search("fundCode\s*=\s*(\w+)", href)
            if not findProId:
                continue
            item['fund_code'] = findProId.group(1)

            print item
            yield item

            # 历史净值
            url = "http://www.ciit.com.cn/funds-struts/fund-net-chart-table/{}?page=1-16".format(item['fund_code'])
            yield scrapy.Request(url, callback=lambda response, item=item: self.parse_history_link(response, item))


    def parse_history_link(self, response, item):
        self.log(response.url)

        # 获取当前页的历史净值
        yield scrapy.Request(response.url,
                             callback=lambda response, item=item: self.parse_history_nav(response, item),
                             dont_filter=True)

        # 翻页
        urls = response.xpath('//a[contains(@href, "/funds-struts/fund-net-chart-table/")]/@href').extract()
        for url in set(urls):
            url = url if 'http' in url else "http://www.ciit.com.cn" + url
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
            if len(tds) != 2 or tds[0].text == '日期':
                continue

            item = FundSpiderItem()
            item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = itemTop['fund_name']
            item['fund_full_name'] = itemTop['fund_full_name']
            item['nav'] = tds[1].text.strip()
            # item['added_nav'] = tds[2].text.strip()
            item['foundation_date'] = itemTop['foundation_date']
            item['statistic_date'] = tds[0].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = response.url
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_full_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item['fund_name'], item['statistic_date']
            yield item





