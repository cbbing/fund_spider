# -*- coding: utf-8 -*-
"""
华宝信托
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


class TrustHuabaoSpider(scrapy.Spider):
    name = "trust_huabao_spider"
    allowed_domains = ["huabaotrust.com"]

    start_urls = (
        'http://www.huabaotrust.com/index111.jsp',
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

            url = "http://www.huabaotrust.com/index111.jsp"
            for i in range(2, page_count+1):
                formdata = {"show": "0",
                            "pageIndex": str(i),
                            "totalSize": "77",
                            }
                yield FormRequest(url, callback=self.parse_item, formdata=formdata)

        # for page in response.xpath('//div[@class="pagebar"]/a'):
        #     link = page.xpath('@href').extract()[0]
        #     if 'http' not in link:
        #         link = "http://trust.ecitic.com/XXPL_JZPL/" + link
        #
        #     self.log(link)
        #     print link
        #     yield scrapy.Request(link, callback=self.parse_item)


    def parse_item(self, response):
        soup = bs(response.body, 'lxml')

        trs = soup.find_all('tr')
        if len(trs) > 3:
            print trs[2].text
        return

        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 4 or tds[0].text == '产品ID':
                continue

            item = FundSpiderItem()
            item['fund_id'] = tds[0].text.strip()
            item['fund_name'] = tds[1].text.strip()
            # item['fund_full_name'] = ''
            # item['open_date'] = tds[2].text.strip()
            item['nav'] = tds[2].text.strip()
            # item['added_nav'] = tds[4].text.strip()
            # item['foundation_date'] = tds[6].text.strip()
            item['statistic_date'] = tds[3].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = 'http://www.huabaotrust.com/index111.jsp'
            item['org_id'] = 'TG0002'



            item['uuid'] = hashlib.md5((item['fund_name']+item['statistic_date']).encode('utf8')).hexdigest()
            # print item
            # yield item

            # 产品详情
            href = tds[1].find('a')['href']
            if 'http' not in href:
                href = "http://www.huabaotrust.com" + href
            yield scrapy.Request(href, callback=lambda response, item=item : self.parse_detail(response, item))


    def parse_item_plus(self, response, item):
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        if len(trs) == 6:
            tds = trs[2].find_all('td')
            if len(tds) and tds[0].text.strip() == "产品建立日期":
                item['foundation_date'] = tds[1].text.strip()

        print item
        yield item


    def parse_detail(self, response, itemTop):
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('ul')
        for tr in trs:
            tds = tr.find_all('li')
            if len(tds) != 4 or tds[0].text == '估值基准日':
                continue

            item = FundSpiderItem()
            # item['fund_id'] = ''
            item['fund_name'] = itemTop['fund_name']
            item['fund_full_name'] = "中信信托." + item['fund_name'] + "证券投资集合资金信托"
            item['open_date'] = itemTop['open_date']
            item['nav'] = tds[1].text.strip()
            # item['added_nav'] =
            item['foundation_date'] = itemTop['foundation_date']
            item['statistic_date'] = tds[0].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = itemTop['source']
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item


