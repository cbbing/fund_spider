# -*- coding: utf-8 -*-
"""
外贸信托
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


class TrustFoticSpider(scrapy.Spider):
    name = "trust7_fotic_spider"
    allowed_domains = ["fotic.com.cn"]

    # start_urls = (
    #     'http://www.crctrust.com/servlet/json',
    # )

    def start_requests(self):
        url = "http://www.fotic.com.cn/DesktopModules/ProductJZ/GetJsonResult.ashx"
        requests = []
        formdata = {"programName": "",
                    "sDate": "",
                    "eDate": "",
                    "pageNo": "1",
                    "pageSize": "10"
                    }

        request = FormRequest(url, callback=self.parse, formdata=formdata)
        requests.append(request)
        return requests


    def parse(self, response):
        self.log(response.url)

        # 请求第一页
        formdata = {"programName": "",
                    "sDate": "",
                    "eDate": "",
                    "pageNo": "1",
                    "pageSize": "10"
                    }
        yield FormRequest(response.url, formdata=formdata, callback=self.parse_item, dont_filter=True)


        # 请求其它页
        encodejson = json.loads(response.body, encoding='utf8')
        totalPages = encodejson['totalCount']
        for i in range(2, totalPages+1):
            formdata = {"programName": "",
                        "sDate": "",
                        "eDate": "",
                        "pageNo": str(i),
                        "pageSize": "10"
                        }
            yield FormRequest(response.url, callback=self.parse_item, formdata=formdata, dont_filter=True)


    def parse_item(self, response):
        self.log(response.url)
        # print response.url
        # return

        encodejson = json.loads(response.body, encoding='utf8')
        datas = encodejson['result']

        for data in datas:

            item = FundSpiderItem()

            # item['fund_id'] = data['jjdm'].strip()
            item['fund_code'] = data['projectcode']
            item['fund_name'] = data['projectnameshort']
            item['fund_full_name'] = data['projectname']
            # item['open_date'] = tds[2].text.strip()
            item['nav'] = data['netvalue'].strip()
            item['added_nav'] = data['totalnetvalue']
            # item['foundation_date'] = data['sxrq']
            item['statistic_date'] = data['date']


            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = "http://www.fotic.com.cn/tabid/141/Default.aspx"
            item['org_id'] = 'TG0007'


            item['uuid'] = hashlib.md5((item['fund_name']+item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item





