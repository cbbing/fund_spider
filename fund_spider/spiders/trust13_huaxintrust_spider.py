# -*- coding: utf-8 -*-
"""
华信信托
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
from util.date_convert import GetNowTime


class TrustHuaxinSpider(scrapy.Spider):
    name = "trust13_spider"
    allowed_domains = ["huaxintrust.com"]

    start_urls = (
        'http://www.huaxintrust.com/news2.asp?nid=36-46',
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
        # yield scrapy.Request(response.url, callback=self.parse_item)

        # 请求所有分页
        hrefs = response.xpath('//a[contains(@href, "&nid=36-46")]/@href').extract()
        for href in set(hrefs):
            if 'http' not in href:
                href = "http://www.huaxintrust.com/news2.asp" + href

            yield scrapy.Request(href, callback=self.parse_item)

            yield scrapy.Request(href, callback=self.parse)



    def parse_item(self, response):
        self.log(response.url)

        # 请求所有产品详情
        hrefs = response.xpath('//a[contains(@href, "newsshow2.asp?nid=")]/@href').extract()
        for href in hrefs:
            if 'http' not in href:
                href = "http://www.huaxintrust.com/" + href
            yield scrapy.Request(href, callback=self.parse_history_nav)

        # soup = bs(response.body, 'lxml')
        #
        # hrefs = soup.find_all('a')
        #
        # trs = soup.find_all('li')
        # for tr in trs:
        #
        #
        #
        #     tds = tr.find_all('td')
        #     if len(tds) != 4 or tds[0].text == '产品ID':
        #         continue
        #
        #     item = FundSpiderItem()
        #     item['fund_code'] = tds[0].text.strip()
        #     item['fund_name'] = tds[1].text.strip()
        #     # item['fund_full_name'] = ''
        #     # item['open_date'] = tds[2].text.strip()
        #     item['nav'] = tds[2].text.strip()
        #     # item['added_nav'] = tds[4].text.strip()
        #     # item['foundation_date'] = tds[6].text.strip()
        #     item['statistic_date'] = tds[3].text.strip()
        #
        #     item['entry_time'] = GetNowTime()
        #     item['source_code'] = 1
        #     item['source'] = response.url
        #     item['org_id'] = 'TG0002'
        #
        #
        #
        #     item['uuid'] = hashlib.md5((item['fund_name']+item['statistic_date']).encode('utf8')).hexdigest()
        #     # print item
        #     # yield item
        #
        #     # 产品详情
        #     href = tds[1].find('a')['href']
        #     if 'http' not in href:
        #         href = "http://www.huabaotrust.com" + href
        #     yield scrapy.Request(href, callback=lambda response, item=item : self.parse_item_plus(response, item))



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
    #
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
    #     pageFind = re.search("共\s*(\d+)\s*页", response.body)  # 获取页数
    #     if pageFind:
    #         page_count = int(pageFind.group(1))
    #
    #         for i in range(2, page_count + 1):
    #             formdata = {"show": "0",
    #                         "pageIndex": str(i),
    #                         "totalSize": "100",
    #                         }
    #             yield FormRequest(response.url, callback=lambda response, itemTop=itemTop: self.parse_history_nav(response, itemTop), formdata=formdata, dont_filter=True)

    def parse_history_nav(self, response):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)

        soup = bs(response.body, 'lxml')

        statistic_date = ''
        centers = soup.find_all('div', {'align':'center'})
        for center in centers:
            if '日期' in center.text:
                d = center.find_all('b')
                if len(d)==2:
                    statistic_date = d[1].text
                    break

        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 4 or tds[0].text.strip() == '信托计划名称':
                continue

            item = FundSpiderItem()
            # item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = tds[0].text.strip()
            item['fund_full_name'] = item['fund_name']
            item['nav'] = tds[2].text.strip()
            item['added_nav'] = tds[3].text.strip()
            item['foundation_date'] = tds[1].text.strip()
            item['statistic_date'] = statistic_date

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = "TG0013"

            item['uuid'] = hashlib.md5((item['fund_full_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item


