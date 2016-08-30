# -*- coding: utf-8 -*-
"""
万向信托
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
import re
import hashlib
from scrapy.http import FormRequest
from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
class TrustSxxtSpider(scrapy.Spider):
    name = "trust61_wx_spider"
    allowed_domains = ["wxtrust.com"]

    start_urls = (
        'http://www.wxtrust.com/c55ef089-7d41-4e6c-8439-e5694694365e/index.html',
    )


    def parse(self, response):
        self.log(response.url)
        # 请求第一页
        yield scrapy.Request(response.url, callback=self.parse_two, dont_filter=True)

        # html = requests.get(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find('span', id="PageSpan").find_all("a")
        t = trs[1]['href']
        ts=filter(str.isdigit, t)
        for i in range(1,int(ts)+1):
            url = "http://www.wxtrust.com/c55ef089-7d41-4e6c-8439-e5694694365e/index_%d.html"%i
            yield scrapy.Request(url, callback=self.parse_two)

    def parse_two(self,response):
        self.log(response.url)
        # html = requests.get(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('input',{"name":"hidTitle"})
        urls="http://www.wxtrust.com/c55ef089-7d41-4e6c-8439-e5694694365e/info/2016/"
        for tr in trs:
            item = FundSpiderItem()
            item['fund_code']=tr['id'].replace("h_","")

            item['fund_name'] =tr['value'].replace('净值报告','')
            item['fund_full_name'] = item['fund_name']
            print item

            urll=urls + item['fund_code']+".html"
            yield scrapy.Request(urll, callback=lambda response, item=item : self.parse_history_nav(response, item))



    def parse_history_nav(self, response,itemTop):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        # html = requests.get(response.url)
        soup = BeautifulSoup(response.body, "lxml")

        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds)==4:
                item = FundSpiderItem()
                item['fund_code'] = itemTop['fund_code']
                item['fund_name'] = itemTop['fund_name']
                item['fund_full_name'] = itemTop['fund_full_name']
                item['nav'] = tds[1].text.strip()
                item['added_nav']=tds[2].text.strip()
                item['statistic_date'] = tds[0].text.strip()

                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0061"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item