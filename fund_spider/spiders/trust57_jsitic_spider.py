# -*- coding: utf-8 -*-
"""
江苏信托
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
import re,json
import hashlib
from scrapy.http import FormRequest
from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
class TrustSxxtSpider(scrapy.Spider):
    name = "trust57_spider"
    allowed_domains = ["jsitic.net"]

    start_urls = (
        'http://www.jsitic.net/423/220778.html',
    )


    def parse(self, response):
        self.log(response.url)
        html = requests.get(response.url)
        soup = BeautifulSoup(html.text, "lxml")
        trs = soup.find_all('div', style="height:30px;")
        for tr in trs:
            tds = tr.find_all("div")
            if len(tds) == 4:
                item = FundSpiderItem()
                item['fund_full_name'] = tds[0].text.strip().encode("ISO-8859-1")
                item['fund_name'] = tds[0].text.strip().encode("ISO-8859-1").replace(r"江苏信托—","").replace(r"证券投资集合资金信托计划","")

                item['nav'] = tds[2].text.strip().encode("ISO-8859-1")
                item['statistic_date'] = tds[1].text.strip().encode("ISO-8859-1")
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0057"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item



    # def parse_history_nav(self, response):
    #     """
    #     历史净值
    #     :param response:
    #     :param itemTop:
    #     :return:
    #     """
    #     self.log(response.url)
    #     html = requests.get(response.url)
    #     soup = BeautifulSoup(html.text, "lxml")
    #     trs = soup.find_all('div', style="height:30px;")
    #     for tr in trs:
    #         tds = tr.find_all("div")
    #         if len(tds) == 4:
    #             item = FundSpiderItem()
    #             item['fund_full_name'] = tds[0].text.strip().encode("ISO-8859-1")
    #             item['nav'] = tds[2].text.strip().encode("ISO-8859-1")
    #             item['statistic_date'] = tds[1].text.strip().encode("ISO-8859-1")
    #             item['entry_time'] = GetNowTime()
    #             item['source_code'] = 1
    #             item['source'] = response.url
    #             item['org_id'] = "TG0057"
    #             item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
    #             print item
    #             yield item