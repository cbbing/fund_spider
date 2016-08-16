# -*- coding: utf-8 -*-
"""
华润信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy

from bs4 import BeautifulSoup as bs
import re
import hashlib
import json
from scrapy.http import FormRequest

from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime


class TrustCrctrustSpider(scrapy.Spider):
    name = "trust_crctrust_spider"
    allowed_domains = ["crctrust.com"]

    # start_urls = (
    #     'http://www.crctrust.com/servlet/json',
    # )

    def start_requests(self):
        url = "http://www.crctrust.com/servlet/json"
        requests = []
        formdata = {"funcNo": "904005",
                    "page": '1',
                    "numPerPage": "10",
                    "type": "27",
                    "name":"",
                    "order":"sxrq",
                    "sort":"asc"
                   }
        request = FormRequest(url, callback=self.parse, formdata=formdata)
        requests.append(request)
        return requests


    def parse(self, response):
        self.log(response.url)

        # 请求第一页
        # self.parse_item(response)
        formdata = {"funcNo": "904005",
                    "page": '1',
                    "numPerPage": "10",
                    "type": "27",
                    "name": "",
                    "order": "sxrq",
                    "sort": "asc"
                    }
        yield FormRequest(response.url, formdata=formdata, callback=self.parse_item, dont_filter=True)


        # 请求其它页
        encodejson = json.loads(response.body, encoding='utf8')
        totalPages = encodejson['results'][0]['totalPages']
        for i in range(2, totalPages+1):
            url = "http://www.crctrust.com/servlet/json"
            formdata = {"funcNo": "904005",
                        "page": str(i),
                        "numPerPage": "10",
                        "type": "27",
                        "name": "",
                        "order": "sxrq",
                        "sort": "asc"
                        }
            yield FormRequest(url, callback=self.parse_item, formdata=formdata, dont_filter=True)


    def parse_item(self, response):
        self.log(response.url)
        # print response.url
        # return

        encodejson = json.loads(response.body, encoding='utf8')
        datas = encodejson['results'][0]['data']

        for data in datas:

            item = FundSpiderItem()

            item['fund_code'] = data['jjdm'].strip()
            item['fund_name'] = data['jjjc'].strip()
            # item['fund_full_name'] = ''
            # item['open_date'] = tds[2].text.strip()
            item['nav'] = data['nav'].strip()
            # item['added_nav'] = tds[2].text.strip()
            item['foundation_date'] = data['sxrq'].strip()
            item['statistic_date'] = data['tradedate'].strip()


            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = "http://www.crctrust.com/main/ywycp/zqxtjzpl/index.html"
            item['org_id'] = 'TG0006'


            item['uuid'] = hashlib.md5((item['fund_name']+item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item

            # 历史净值
            formdata = {"funcNo": "904007",
                        "page": "1",
                        "numPerPage": "20",
                        "jjdm":item['fund_code'],
                        "startTime": "",
                        "endTime": "",
                        "order_by": "1",
                        }
            yield FormRequest(response.url, callback=lambda response, item=item : self.parse_history_link(response, item),
                              formdata=formdata, dont_filter=True)



    def parse_history_link(self, response, item):
        self.log(response.url)

        # 请求第一页
        # self.parse_history_nav(response, item)
        formdata = {"funcNo": "904007",
                   "page": "1",
                   "numPerPage": "20",
                   "jjdm": item['fund_code'],
                   "startTime": "",
                   "endTime": "",
                   "order_by": "1",
                   }
        yield FormRequest(response.url, callback=lambda response, itemTop=item : self.parse_history_nav(response, itemTop),
                          formdata=formdata, dont_filter=True)


        # 请求其它页
        encodejson = json.loads(response.body, encoding='utf8')
        totalPages = encodejson['results'][0]['totalPages']
        for i in range(2, totalPages + 1):
            formdata = {"funcNo": "904005",
                        "page": str(i),
                        "numPerPage": "10",
                        "type": "27",
                        "name": "",
                        "order": "sxrq",
                        "sort": "asc"
                        }
            yield FormRequest(response.url, callback=lambda response, itemTop=item : self.parse_history_nav(response, itemTop),
                              formdata=formdata, dont_filter=True)


    def parse_history_nav(self, response, itemTop):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)

        encodejson = json.loads(response.body, encoding='utf8')
        datas = encodejson['results'][0]['data']

        for data in datas:

            item = FundSpiderItem()
            item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = itemTop['fund_name']
            item['nav'] = data['nav'].strip()
            # item['added_nav'] = tds[2].text.strip()
            item['foundation_date'] = itemTop['foundation_date']
            item['statistic_date'] = data['tradedate'].strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = itemTop['source']
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item


