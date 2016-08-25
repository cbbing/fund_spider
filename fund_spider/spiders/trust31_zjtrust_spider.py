# -*- coding: utf-8 -*-
"""
紫金信托
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


class TrustZjSpider(scrapy.Spider):
    name = "trust31_zjtrust_spider"
    allowed_domains = ["zjtrust.com.cn"]

    start_urls = (
        'http://www.zjtrust.com.cn/cn/page/41.html',
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
    #     pageFind = re.search("1\/(\d+)\s*页", response.body)# 获取页数
    #     if pageFind:
    #         page_count = int(pageFind.group(1))
    #         for i in range(2, page_count+1):
    #             url = "http://www.huaao-trust.com/list/705/{}.shtml".format(i)
    #             yield scrapy.Request(url, callback=self.parse_item)



    def parse(self, response):
        self.log(response.url)

        hrefs = response.xpath("//a[contains(@href, '/cn/page/41/')]/@href").extract()
        for href in hrefs:
            href = href if 'http' in href else "http://www.zjtrust.com.cn" + href
            yield scrapy.Request(href, callback=self.parse_history_nav)



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
    #     # 请求所有页
    #     pageFind = re.search("共\d\/(\d+)页", response.body)  # 获取页数
    #     if pageFind:
    #         page_count = int(pageFind.group(1))
    #         for i in range(1, page_count + 1):
    #             href = "http://www.zhtrust.com/front/fund/Product/findProductNet.do?gotoPage={}".format(i)
    #             formdata = {
    #                 "fundcode": itemTop['fund_code']
    #             }
    #             yield FormRequest(href,
    #                               formdata=formdata,
    #                               callback=lambda response, item=itemTop: self.parse_history_nav(response, item),
    #                               dont_filter=True)


    def parse_history_nav(self, response):
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
            if len(tds) != 3 or tds[0].text == '产品名称':
                continue

            item = FundSpiderItem()
            # item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = tds[0].text.strip()
            item['fund_full_name'] = item['fund_name']
            item['nav'] = tds[1].text.strip()
            item['statistic_date'] = tds[2].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = "TG0031"

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item

