# -*- coding: utf-8 -*-
"""
昆仑信托
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


class TrustSxxtSpider(scrapy.Spider):
    name = "trust26_kunluntrust_spider"
    allowed_domains = ["kunluntrust.com"]

    start_urls = (
        'http://www.kunluntrust.com/xinxipilu/chanpinxinxi/chanpinjingzhi/',
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
        yield scrapy.Request(response.url, callback=self.parse_item, dont_filter=True)

        # 请求其它页
        hrefs = response.xpath("//li/a[contains(@href, 'list_32_')]/@href").extract()
        for href in hrefs:
            href = href if 'http' in href else "http://www.kunluntrust.com/xinxipilu/chanpinxinxi/chanpinjingzhi/" + href
            yield scrapy.Request(href, callback=self.parse_item)


    def parse_item(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')

        dts = soup.find_all('dt', {'class':re.compile('name|other')})
        for i in range(len(dts)):

            #cs = dts[i]['class'] # type: list
            if dts[i]['class'][0] == 'name' and dts[i].text.strip() != '产品名称':
                if i+2 < len(dts) and dts[i+2]['class'][0] == 'other':

                    item = FundSpiderItem()
                    # item['fund_code'] = tds[0].text.strip()
                    fund_name = dts[i].text.strip()
                    fund_name = fund_name.split('第')[0]
                    fund_name = fund_name.replace('信息披露净值公告 ','')
                    item['fund_name'] = fund_name
                    item['fund_full_name'] = item['fund_name']
                    # item['open_date'] = tds[2].text.strip()
                    item['nav'] = dts[i+1].text.strip()
                    # item['added_nav'] = tds[2].text.strip()
                    # item['foundation_date'] = tds[6].text.strip()
                    item['statistic_date'] = dts[i+2].text.strip()

                    item['entry_time'] = GetNowTime()
                    item['source_code'] = 1
                    item['source'] = response.url
                    item['org_id'] = 'TG0026'

                    # href = tds[0].find('a')['href']
                    # findProId = re.search("fundcode=(\w+)", href)
                    # if not findProId:
                    #     continue
                    # print findProId.group(1)
                    # item['fund_code'] = findProId.group(1)

                    item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                    print item
                    yield item

                    # 产品详情

                    # href = "http://www.zhtrust.com/front/fund/Product/findProductNet.do?gotoPage=1"  #
                    # formdata = {
                    #     "fundcode": item['fund_code']
                    # }
                    # if 'http' not in href:
                    #     href = "http://www.huabaotrust.com" + href
                    # yield FormRequest(href, formdata=formdata,
                    #                   callback=lambda response, item=item: self.parse_history_link(response, item))

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
    #     trs = soup.find_all('tr')
    #     first_col = '产品名称'
    #     for tr in trs:
    #         tds = tr.find_all('td')
    #         if len(tds) not in (4,5):
    #             continue
    #         if '名称' in tds[0].text.strip() or '日期' in tds[0].text.strip():
    #             first_col = tds[0].text.strip()
    #             continue
    #
    #         item = FundSpiderItem()
    #         # item['fund_code'] = itemTop['fund_code']
    #         if first_col != '日期':
    #             item['fund_name'] = tds[0].text.strip()
    #             item['fund_full_name'] = item['fund_name']
    #             item['nav'] = tds[3].text.strip()
    #             if len(tds) == 5:
    #                 item['added_nav'] = tds[4].text.strip()
    #             item['foundation_date'] = tds[1].text.strip()
    #             item['statistic_date'] = tds[2].text.strip()
    #         else:
    #             item['fund_name'] = tds[1].text.strip()
    #             item['fund_full_name'] = item['fund_name']
    #             item['nav'] = tds[4].text.strip()
    #             item['foundation_date'] = tds[2].text.strip()
    #             item['statistic_date'] = tds[0].text.strip()
    #
    #         item['entry_time'] = GetNowTime()
    #         item['source_code'] = 1
    #         item['source'] = response.url
    #         item['org_id'] = "TG0024"
    #
    #         item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
    #         print item
    #         yield item

