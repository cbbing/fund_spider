# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import hashlib
import datetime

from fund_spider.items import FundNvDataItem
from scrapy.http import  FormRequest
import requests,json
from util.date_convert import GetNowTime
class TrustSxxtSpider(scrapy.Spider):
    name = "ziguan_fund_nv_data_spider"
    allowed_domains = ["ziguan123.com"]

    def start_requests(self):
        url = 'http://www.ziguan123.com/ajax/productrank'
        requests = []
        formdata = {
            "operator_type": "27",
            "policyfirstlevel": "89,90,91,92,93",
            "policy": "0",
            "fundtype": "",
            "terms": "1",
            "sermonth": "2016-08",
            "sort_name": "Month1",
            "sort_type": "desc",
            "page_index": "1",
            "page_size": "40"
                   }
        request = FormRequest(url, callback=self.parse, formdata=formdata)
        requests.append(request)
        return requests


    def parse(self, response):
        self.log(response.url)

        t = json.loads(response.body)
        #li = t['rawdata']['data']
        pages = t['rawdata']['data'][0]['operator_type']
        for i in range(1, int(pages) + 1):
            data = {  # 表单
                "operator_type": pages,
                "policyfirstlevel": "89,90,91,92,93",
                "policy": "0",
                "fundtype": "",
                "terms": "1",
                "sermonth": "2016-08",
                "sort_name": "Month1",
                "sort_type": "desc",
                "page_index": str(i),
                "page_size": "40"
            }
            yield scrapy.FormRequest(response.url, formdata=data, callback=self.parse_item, dont_filter=True)
            break

    def parse_item(self, response):
        print response.url

        t = json.loads(response.body)
        datas = t['rawdata']['data']
        for data in datas:
            url = "http://www.ziguan123.com/product/detail/" + data['id']
            yield scrapy.Request(url, callback=self.parse_item_detail)
            break

    def parse_item_detail(self,response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all("td", align="left")
        if len(trs) > 0:
            for tr in trs:
                urll = "http://www.ziguan123.com" + tr.a['href']
                yield scrapy.Request(urll, callback=self.parse_detail, dont_filter=True)

        else:
            yield scrapy.Request(response.url, callback=self.parse_detail, dont_filter=True)

    def parse_detail(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        title = soup.find("h1", {"class": "cp-title"})
        if title:
            print title.text
            print response.url
            num = response.url.replace("http://www.ziguan123.com/product/detail/", "")

            item = FundNvDataItem()

            url = "http://www.ziguan123.com/product/ajaxlinechart"
            data = {  # 表单
                "productid": num,
            }
            yield scrapy.FormRequest(url, formdata=data,
                                     callback=lambda response, title=title, num=num : self.parse_detail_nav(response, title, num))


    def parse_detail_nav(self, response, title):
        print response.url
        soup = BeautifulSoup(response.text, "lxml")
        tt = json.loads(soup.text)
        for i in tt['data']:
            item = FundNvDataItem()
            # 将时间撮换为标准时间
            timeStamp = int(i['valuedate']) / 1000
            dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
            otherStyleTime = dateArray.strftime("%Y-%m-%d")
            item['fund_name'] = title.text
            item['fund_full_name'] = title.text
            item['fund_id'] = num
            item['nav'] = i['netunit']
            item['swanav'] = i['totalnet']
            item['statistic_date'] = otherStyleTime
            item['entry_time'] = GetNowTime()
            item['source_code'] = "3-第三方"
            item['data_source'] = 6
            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item






