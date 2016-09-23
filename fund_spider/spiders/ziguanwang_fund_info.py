# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import hashlib

from fund_spider.items import FundInfoItem
from scrapy.http import  FormRequest
import requests,json
from util.date_convert import GetNowTime
class TrustSxxtSpider(scrapy.Spider):
    name = "ziguan_fund_info_spider"
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
        item = FundInfoItem()
        soup = BeautifulSoup(response.body, "lxml")
        title = soup.find("h1", {"class": "cp-title"})
        if title:
            num = response.url.replace("http://www.ziguan123.com/product/detail/", "")
        ss = soup.find("li", {"class": "li_onfor_01"})
        t = ss.text.split()[1]
        fund_status = t.replace("运行状态：", "")
        item['fund_id'] = num
        item['fund_name'] = title.text
        item['fund_full_name'] = title.text
        item['fund_status'] = fund_status
        rs = soup.find("table", {"class": "tablebor_xy table_td_w25p "})
        trs = rs.find_all("tr")
        tds = trs[1].find_all("td")
        item['fund_manager'] = tds[1].text.strip()
        item['fund_member'] = tds[3].text.strip()

        tds = trs[2].find_all("td")
        item['fund_type_issuance'] = tds[1].text.strip()
        item['foundation_date'] = tds[3].text.strip()

        tds = trs[3].find_all("td")
        item['duration'] = tds[3].text.strip().replace("--", "")

        tds = trs[4].find_all("td")
        item['fund_stockbroker'] = tds[1].text.strip().replace("--", "")
        item['fund_custodian'] = tds[3].text.strip().replace("--", "")

        tds = trs[5].find_all("td")
        item['min_purchase_amount'] = tds[1].text.strip()
        item['init_total_asset'] = tds[3].text.strip()

        tds = trs[6].find_all("td")
        item['locked_time_limit'] = tds[1].text.strip().replace("--", "")
        item['open_date'] = tds[3].text.strip().replace("--", "")

        tds = trs[7].find_all("td")
        item['fee_subscription'] = tds[1].text.strip().replace("--", "")
        item['fee_redeem'] = tds[3].text.strip().replace("--", "")

        tds = trs[8].find_all("td")
        item['fee_manage'] = tds[1].text.strip().replace("--", "")
        item['fee_pay'] = tds[3].text.strip().replace("--", "")
        item['type_name'] = "CTA策略|股票对冲|组合基金|全球宏观|债券策略"
        item['entry_time'] = GetNowTime()
        item['uuid'] = hashlib.md5((item['fund_name'] + item['fund_id']).encode('utf8')).hexdigest()
        print item
        yield item








