# -*- coding: utf-8 -*-
"""
大业信托
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
from scrapy import Selector

from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime


class TrustDytrusteeSpider(scrapy.Spider):
    name = "trust43_spider"
    allowed_domains = ["dytrustee.com"]

    start_urls = (
        'http://www.dytrustee.com/xxpl/jzgg/',
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
        sel = Selector(text=response.body, type="html")
        hrefs = sel.xpath('//a[re:test(@href, "^/xxpl/jzgg/\d+")]//@href').extract()
        for href in hrefs:
            href = "http://www.dytrustee.com" + href
            yield scrapy.Request(href, callback=self.parse_item)


    def parse_item(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')

        trs = soup.find_all('tr')

        fund_name = None
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) not in (3, 4) or tds[0].text.strip() == '产品名称':
                continue

            if len(tds[0].text.strip()):
                fund_name = tds[0].text.strip()
                break

        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) not in (2, 3, 4) or '估值' in tds[-1].text.strip():
                continue

            item = FundSpiderItem()
            # item['fund_code'] = tds[0].text.strip()
            item['fund_name'] = fund_name
            item['fund_full_name'] = item['fund_name']
            # item['open_date'] = tds[2].text.strip()
            if len(tds) == 4:
                item['nav'] = tds[1].text.strip()
                # item['added_nav'] = tds[2].text.strip()
                # item['foundation_date'] = tds[6].text.strip()
                item['statistic_date'] = tds[3].text.strip().replace('年','-').replace('月','-').replace('日','')
            else:
                item['nav'] = tds[-2].text.strip()
                item['statistic_date'] = tds[-1].text.strip().replace('年', '-').replace('月', '-').replace('日', '')


            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = 'TG0043'

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item

        if not trs:
            ps = soup.find_all('p', {'class':'MsoNormal'})
            for p in ps:
                row_data = p.text.strip()
                if row_data:
                    if '产品名称' in row_data:
                        continue
                    print row_data
                    row1 = re.sub('[ \t\n]+', ':', row_data)
                    datas = re.split(u'[  \t\n]+', row_data)
                    if len(datas) == 3:
                        item = FundSpiderItem()
                        item['fund_name'] = datas[0]
                        item['fund_full_name'] = item['fund_name']
                        item['nav'] = datas[1]
                        item['statistic_date'] = datas[2].replace('/', '-')

                        item['entry_time'] = GetNowTime()
                        item['source_code'] = 1
                        item['source'] = response.url
                        item['org_id'] = 'TG0043'

                        item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                        print item
                        yield item


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


    # def parse_history_nav(self, response):
    #     """
    #     历史净值
    #     :param response:
    #     :param itemTop:
    #     :return:
    #     """
    #     self.log(response.url)
    #
    #     soup = bs(response.body, 'lxml')
    #     infos = soup.find('div', {'id':'infoContent'})
    #     if infos:
    #         data = infos.text
    #         datas = [d.strip() for d in data.split('\n') if len(d.strip())>0]
    #         for data in datas:
    #             print data
    #         if len(datas) == 4:
    #             item = FundSpiderItem()
    #             item['fund_name'] = datas[0]
    #             item['fund_full_name'] = item['fund_name']
    #             item['nav'] = datas[2]
    #             item['statistic_date'] = datas[3]
    #
    #             item['entry_time'] = GetNowTime()
    #             item['source_code'] = 1
    #             item['source'] = response.url
    #             item['org_id'] = "TG0039"
    #
    #             item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
    #             print item
    #             yield item




