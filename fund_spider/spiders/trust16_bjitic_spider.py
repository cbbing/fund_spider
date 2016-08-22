# -*- coding: utf-8 -*-
"""
北京信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy
import math
from bs4 import BeautifulSoup as bs
import re
import hashlib
import random
from scrapy.http import FormRequest
from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime


class TrustPinganSpider(scrapy.Spider):
    name = "trust16_bjitic_spider"
    allowed_domains = ["bjitic.com"]

    start_urls = (
        'http://www.bjitic.com/asp/YG/getProb.asp',
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


    # def parse(self, response):
    #     self.log(response.url)
    #
    #     # 请求第一页
    #     yield scrapy.Request(response.url, callback=self.parse_item, dont_filter=True)
    #
    #     # 请求其它页
    #     soup = bs(response.body, 'lxml')
    #     pageSum = soup.find('input', {'name':'totalRows'})
    #     if pageSum:
    #         page_count = math.ceil(float(pageSum['value'])/15.)
    #         page_count = int(page_count)
    #         for i in range(2, page_count+1):
    #             formdata = {"trustNo": "",
    #                         "trustName": "",
    #                         "currentPageNo": str(i),
    #                         "cooID": "",
    #                         "type": "",
    #                         }
    #             yield FormRequest(response.url, callback=self.parse_item, formdata=formdata, dont_filter=True)


    def parse(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')

        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 3 or tds[0].text.strip() == '产品名称':
                continue

            item = FundSpiderItem()
            # item['fund_code'] = tds[0].text.strip()
            item['fund_name'] = tds[0].text.strip()
            # item['fund_full_name'] = ''
            # item['open_date'] = tds[2].text.strip()
            # item['nav'] = tds[2].text.strip()
            # item['added_nav'] = tds[3].text.strip()
            item['foundation_date'] = tds[1].text.strip()
            # item['statistic_date'] = tds[5].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = 'TG0016'

            href = tds[0].find('a')['href']
            findProId = re.search("\/news\/web-10-1-3\/\?id=(\w+)", href)
            if not findProId:
                continue
            # print findProId.group(1)
            item['fund_code'] = findProId.group(1)


            # item['uuid'] = hashlib.md5((item['fund_name']+item['statistic_date']).encode('utf8')).hexdigest()
            print item
            # yield item

            # 产品详情
            url = "http://www.bjitic.com/asp/YG/getPro2.asp?id={}&no-cache={}".format(item['fund_code'], random.random())
            yield scrapy.Request(url, callback=lambda response, item=item : self.parse_history_nav(response, item))


    # def parse_item_plus(self, response, item):
    #     self.log(response.url)
    #
    #     soup = bs(response.body, 'lxml')
    #     trs = soup.find_all('tr')
    #     if len(trs) == 6:
    #         tds = trs[2].find_all('td')
    #         if len(tds) and tds[0].text.strip() == "产品建立日期":
    #             item['foundation_date'] = tds[1].text.strip()
    #
    #     print item
    #     yield item
    #
    #     # 产品历史净值
    #     href_history = "http://www.huabaotrust.com/mouyichanpinlishi.jsp?product_id={fund_code}&prod_period_no=0001". \
    #         format(fund_code=item['fund_code'])
    #     yield scrapy.Request(href_history, callback=lambda response, itemTop=item: self.parse_history_link(response, itemTop))

    # def parse_history_link(self, response, itemTop):
    #     """
    #     历史净值链接
    #     :param response:
    #     :param itemTop:
    #     :return:
    #     """
    #
    #     self.log(response.url)
    #
    #     # 第一页
    #     yield scrapy.Request(response.url, callback=lambda response, itemTop=itemTop: self.parse_history_nav(response, itemTop), dont_filter=True)
    #
    #     # 请求其它页
    #     soup = bs(response.body, 'lxml')
    #     pageSum = soup.find('input', {'name': 'allPage'})
    #     if pageSum:
    #         page_count = int(pageSum['value'])
    #         for i in range(2, page_count + 1):
    #             url = "http://trust.pingan.com/xintuochanpin/jingzhi/{}_000500_temp_{}.shtml".format(itemTop['fund_code'], i)
    #
    #             formdata = {"trustNo": itemTop['fund_code'],
    #                         "childTrustNo": "",
    #                         "pageNo": str(i),
    #                         "startDate": "",
    #                         "endDate": "",
    #                         "pageSum": "",
    #                         "allPage": str(page_count)
    #                         }
    #             yield FormRequest(url, callback=lambda response,item=itemTop : self.parse_history_nav(response, item), formdata=formdata, dont_filter=True)

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
            if len(tds) != 3:
                continue
            find = re.search('\d{4}-\d{2}-\d{2}',  tds[0].text.strip())
            if not find:
                continue

            item = FundSpiderItem()
            # item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = itemTop['fund_name']
            item['nav'] = tds[1].text.strip()
            item['added_nav'] = tds[2].text.strip()
            item['foundation_date'] = itemTop['foundation_date']
            item['statistic_date'] = tds[0].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = response.url
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item['fund_name'],item['statistic_date']
            yield item


