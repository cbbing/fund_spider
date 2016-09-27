# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import hashlib
from fund_spider.items import FundPersonItem
from scrapy.http import  FormRequest
import json
from util.date_convert import GetNowTime
class TrustSxxtSpider(scrapy.Spider):
    name = "ziguan_fund_person_spider"
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
        t = json.loads(response.body)
        datas = t['rawdata']['data']
        for data in datas:
            url = "http://www.ziguan123.com/product/detail/" + data['id']
            yield scrapy.Request(url, callback=self.parse_item_detail)


    def parse_item_detail(self,response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all("td", align="left")
        if len(trs) > 0:
            for tr in trs:
                urll = "http://www.ziguan123.com" + tr.a['href']
                yield scrapy.Request(urll, callback=self.parse_detail,dont_filter=True)

        else:
            yield scrapy.Request(response.url, callback=self.parse_detail, dont_filter=True)


    def parse_detail(self, response):
        self.log(response.url)
        item = FundPersonItem()
        soup = BeautifulSoup(response.body, "lxml")
        title = soup.find("h1", {"class": "cp-title"})
        if title:
            num = response.url.replace("http://www.ziguan123.com/product/detail/", "")
        rs = soup.find("table", {"class": "tablebor_xy table_td_w25p "})
        trs = rs.find_all("tr")
        tds = trs[1].find_all("td")
        d = soup.find("div", {"class": "swiper-slide jjjlbox "})
        if len(d.text.strip()) == 0:
            item['resume'] = d.text.strip()
        if len(d.text.strip().split()) == 1:
            item['resume'] = "None"
        if len(d.text.strip().split()) == 2:
            item['resume'] = d.text.strip().split()[1]
        item['user_name'] = tds[3].text.strip().replace('--', '')
        if len(item['user_name']) == 0:
            return

        item['user_id'] = num

        item['entry_time'] = GetNowTime()
        item['data_source'] = 6
        item['data_source_name'] = '期货资管网'

        item['uuid'] = hashlib.md5((item['user_name']).encode('utf8')).hexdigest()
        print item
        yield item







