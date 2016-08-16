# -*- coding: utf-8 -*-
"""
山东信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy

from bs4 import BeautifulSoup as bs
import re
import hashlib
from scrapy.http import FormRequest

from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime


class TrustSiticSpider(scrapy.Spider):
    name = "trust4_sitic_spider"
    allowed_domains = ["sitic.com.cn"]

    start_urls = (
        'http://www.sitic.com.cn/chart-web/chart/trustnettable!getAllProductNetValue?fundcode=&from=&to=&pages=1-15&fundname=',
    )

    # def start_requests(self):
    #     url = "http://www.huabaotrust.com/index111.jsp"
    #     requests = []
    #     for i in range(1, 7):
    #         formdata = {"show": "0",
    #                     "pageIndex": str(i),
    #                     "totalSize": "30",
    #                    }
    #         request = FormRequest(url, callback=self.parse, formdata=formdata)
    #         requests.append(request)
    #     return requests


    def parse(self, response):
        self.log(response.url)

        # 请求第一页
        yield scrapy.Request(response.url, callback=self.parse_item)

        # 请求其它页
        pageFind = re.search("共\s*(\d+)\s*页", response.body)# 获取页数
        if pageFind:
            page_count = int(pageFind.group(1))

            for i in range(2, page_count+1):
                url = "http://www.sitic.com.cn/chart-web/chart/trustnettable!getAllProductNetValue?fundcode=&from=&to=&pages={}-15&fundname=".format(i)
                yield scrapy.Request(url, callback=self.parse_item)


    def parse_item(self, response):
        self.log(response.url)
        # print response.url
        # return

        soup = bs(response.body, 'lxml')

        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 4 or tds[0].text == '产品名称':
                continue

            item = FundSpiderItem()

            item['fund_name'] = tds[0].text.strip()
            # item['fund_full_name'] = ''
            # item['open_date'] = tds[2].text.strip()
            item['nav'] = tds[1].text.strip()
            item['added_nav'] = tds[2].text.strip()
            # item['foundation_date'] = tds[6].text.strip()
            item['statistic_date'] = tds[3].text.strip()

            # 获取产品ID
            href = tds[1].find('a')['href'] #/products/search/index.html#/sdtrust-web/project/detail!detail?projectCode=SD0ODD&isFund=1
            findProdID = re.search("fundcode=(\w+)", href)
            if findProdID:
                item['fund_code'] = findProdID.group(1)
                print item['fund_code']

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = 'TG0004'



            item['uuid'] = hashlib.md5((item['fund_name']+item['statistic_date']).encode('utf8')).hexdigest()
            # print item
            # yield item

            # 产品详情
            href = "http://www.sitic.com.cn/chart-web/chart/trustnettable?ffshow=&fundcode={}&from=&to=&pages=1-10".format(item['fund_code'])
            yield scrapy.Request(href, callback=lambda response, item=item : self.parse_history_link(response, item))


    def parse_history_link(self, response, item):
        self.log(response.url)

        # 请求第一页
        yield scrapy.Request(response.url, callback=lambda response, item=item : self.parse_history_nav(response, item))

        # 请求其它页
        pageFind = re.search("共\s*(\d+)\s*页", response.body)  # 获取页数
        if pageFind:
            page_count = int(pageFind.group(1))

            for i in range(2, page_count + 1):
                url = "http://www.sitic.com.cn/chart-web/chart/trustnettable?ffshow=&fundcode={}&from=&to=&pages={}-10".format(
                    item['fund_code'],i)
                yield scrapy.Request(url, callback=lambda response, item=item : self.parse_history_nav(response, item))


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
            if len(tds) != 3 or tds[0].text == '日期':
                continue

            item = FundSpiderItem()
            item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = itemTop['fund_name']
            item['nav'] = tds[1].text.strip()
            item['added_nav'] = tds[2].text.strip()
            item['statistic_date'] = tds[0].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = response.url
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item['fund_name'],item['statistic_date']
            yield item


