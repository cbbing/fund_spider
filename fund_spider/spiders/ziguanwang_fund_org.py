# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')# -*- coding: utf-8 -*-
"""

"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import hashlib
import datetime
from fund_spider.items import FundOrgItem
from scrapy.http import  FormRequest
import requests,json
from util.date_convert import GetNowTime

class TrustSxxtSpider(scrapy.Spider):
    name = "ziguan_fund_org_spider"
    allowed_domains = ["ziguan123.com"]

    # start_urls = (
    #     'http://www.ziguan123.com/ajax/productrank',
    # )

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

        t = json.loads(response.text)
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


    def parse_item(self, response):
        print response.url

        t = json.loads(response.text)
        datas = t['rawdata']['data']
        for data in datas:
            url = "http://www.ziguan123.com/product/detail/" + data['id']
            yield scrapy.Request(url, callback=self.parse_detail)



    def parse_detail(self, response):
        self.log(response.url)

        item = FundOrgItem()

        soup = BeautifulSoup(response.body, "lxml")
        title = soup.find("h1", {"class": "cp-title"})
        if title:
            num = response.url.replace("http://www.ziguan123.com/product/detail/", "")

        rs = soup.find("table", {"class": "tablebor_xy table_td_w25p "})
        trs = rs.find_all("tr")
        tds = trs[1].find_all("td")
        # print "投资顾问：" + tds[1].text.strip()
        item['org_full_name'] = tds[1].text.strip()
        item['org_id'] = num
        item['data_source'] = 6
        item['entry_time'] = GetNowTime()
        item['uuid'] = hashlib.md5((item['org_full_name'] + item['org_id']).encode('utf8')).hexdigest()

        d = soup.find("a", {"class": "fblue"})
        if d:
            # print "http://www.ziguan123.com" + d['href']
            url = "http://www.ziguan123.com" + d['href']
            yield scrapy.Request(url, callback=lambda response, item=item : self.parse_detail_plus(response, item))

        else:
            print item
            yield item



    def parse_detail_plus(self,response, item):
        self.log(response.url)

        soup = BeautifulSoup(response.text, "lxml")
        rd = soup.find("p", {"class": "padding20 lineh28"})
        item['profile'] = rd.text
        print item
        yield item





