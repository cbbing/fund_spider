# -*- coding: utf-8 -*-
"""
粤财信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy
import math
from bs4 import BeautifulSoup as bs
import re
import hashlib
from scrapy.http import FormRequest
from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime, GetNowDate


class TrustShanghaiSpider(scrapy.Spider):
    name = "trust20_shanghaitrust_spider"
    allowed_domains = ["shanghaitrust.com"]

    start_urls = (
        'http://www.shanghaitrust.com/products/red/index.html',
        'http://www.shanghaitrust.com/products/purple/index.html',
        'http://www.shanghaitrust.com/products/bojin/index.html',

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

        # 请求所有产品
        hrefs = response.xpath("//a[contains(@href, 'gaikuo/index.html')]/@href").extract()
        # soup = bs(response.body, 'lxml')
        # hrefs = soup.find_all('a', {'href':re.compile('/products/\w+/\w+/gaikuo/index.html')})
        for url in hrefs:
            url = url if 'http' in url else "http://www.shanghaitrust.com" + url
            if 'red' in url or 'purple' in url or 'bojin' in url:
                yield scrapy.Request(url, callback=self.parse_item)

            else:
                url = url.replace('gaikuo', 'netvalue')
                yield scrapy.Request(url, callback=self.parse_item_plus)




    # 红宝石,紫晶石,铂金系列
    def parse_item(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')

        titleBox = soup.find('div', {'class':'product_box_title'})
        if not titleBox:
            return
        #产品名称
        fund_name = titleBox.text

        # 成立日期
        foundation_date = None
        ul = soup.find('ul', {'class':'info_list'})
        if ul:
            lis = ul.find_all('li')
            for li in lis:
                if '成立日期' in li.text:
                    find = re.search('\d{4}-\d{2}-\d{2}', li.text)
                    if find:
                        foundation_date = find.group()
                        break
        if not foundation_date:
            return

        codeFind = re.search('/(\w+)/gaikuo', response.url)
        if not codeFind:
            return
        print codeFind.group(1)

        item = FundSpiderItem()
        item['fund_code'] = codeFind.group(1)
        item['fund_name'] = fund_name
        item['foundation_date'] = foundation_date

        # 产品净值
        href = "http://www.shanghaitrust.com/chart-web/chart/fundnettable?fundcode={}&from={}&to={}&pages=1-100"\
            .format(item['fund_code'], item['foundation_date'], GetNowDate())
        yield scrapy.Request(href, callback=lambda response, item=item: self.parse_history_link(response, item))


    # 现金丰利
    def parse_item_plus(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')

        titleBox = soup.find('div', {'class': 'product_box_title'})
        if not titleBox:
            return
        # 产品名称
        fund_name = titleBox.text

        productIdTag = soup.find('select', {'name':'product'})
        if productIdTag:
            options = productIdTag.find_all('option')
            for op in options:
                item = FundSpiderItem()
                item['fund_code'] = op['value']
                item['fund_name'] = fund_name + op.text

                # 产品净值
                href = "http://www.shanghaitrust.com/chart-web/chart/fundnettable?fundcode={}&from=2006-01-28&to={}&pages=1-100" \
                    .format(item['fund_code'], GetNowDate())
                yield scrapy.Request(href, callback=lambda response, item=item: self.parse_history_link(response, item))

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

    def parse_history_link(self, response, itemTop):
        """
        历史净值链接
        :param response:
        :param itemTop:
        :return:
        """

        self.log(response.url)

        # 第一页
        yield scrapy.Request(response.url, callback=lambda response, itemTop=itemTop: self.parse_history_nav(response, itemTop), dont_filter=True)

        # 请求其它页
        pageFind = re.search("共\s*(\d+)\s*页", response.body)  # 获取页数
        if pageFind:
            page_count = int(pageFind.group(1))

            for i in range(2, page_count + 1):
                url = response.url.replace('&pages=1-100', "&pages={}-100".format(i))
                yield scrapy.Request(url, callback=lambda response,item=itemTop : self.parse_history_nav(response, item), dont_filter=True)

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

            if len(tds) == 3: # 红宝石、绿晶石、铂金
                if tds[0].text.strip() == '日期':
                    continue

                item = FundSpiderItem()
                item['fund_code'] = itemTop['fund_code']
                item['fund_name'] = itemTop['fund_name']
                item['nav'] = tds[1].text.strip()
                item['added_nav'] = tds[2].text.strip()
                item['foundation_date'] = itemTop['foundation_date']
                item['statistic_date'] = tds[0].text.strip()

                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = 'TG0020'

                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item
            elif len(tds) == 4:  # 现金丰利
                if tds[0].text.strip() == '日期':
                    continue

                item = FundSpiderItem()
                item['fund_code'] = itemTop['fund_code']
                item['fund_name'] = itemTop['fund_name']
                item['nav'] = tds[1].text.strip()
                # item['added_nav'] = tds[2].text.strip()
                item['statistic_date'] = tds[0].text.strip()

                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = 'TG0020'

                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item


