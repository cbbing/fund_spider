# -*- coding: utf-8 -*-
"""
北方信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy

from bs4 import BeautifulSoup as bs
import re
import math
import hashlib
from scrapy.http import FormRequest

from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime


class TrustNiticSpider(scrapy.Spider):
    name = "trust39_spider"
    allowed_domains = ["nitic.cn"]

    start_urls = (
        'http://www.nitic.cn/news_list/columnsId=58&&newsCategoryId=8.html',
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

        # 请求所有页
        pageFind = re.search("共\s*([\d,]+)\s*条", response.body)  # 获取页数
        if pageFind:
            COUNT_IN_PAGE = 100
            page_count = pageFind.group(1).replace(',', '')
            page_count = math.ceil(float(page_count)/COUNT_IN_PAGE)
            for i in range(1, int(page_count) + 1):
                url = "http://www.nitic.cn/news_list/columnsId=58&&newsCategoryId=8&FrontNews_list01-002_pageNo={}" \
                      "&FrontNews_list01-002_pageSize={}.html"\
                    .format(i, COUNT_IN_PAGE)
                yield scrapy.Request(url, callback=self.parse_item)


    def parse_item(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')

        a_tags = soup.find_all('a', {'href':re.compile('/news_detail/newsId=\w+.html')})
        for a in a_tags:
            if '净值' in a.text:
                href = "http://www.nitic.cn" + a['href']
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
        infos = soup.find('div', {'id':'infoContent'})
        if infos:
            data = infos.text
            datas = [d.strip() for d in data.split('\n') if len(d.strip())>0]
            for data in datas:
                print data
            if len(datas) == 4:
                item = FundSpiderItem()
                item['fund_name'] = datas[0]
                item['fund_full_name'] = item['fund_name']
                item['nav'] = datas[2]
                item['statistic_date'] = datas[3]

                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0039"

                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item




