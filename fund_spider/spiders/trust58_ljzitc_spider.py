# -*- coding: utf-8 -*-
"""
陆家嘴信托
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
# from webHelper import get_requests
from scrapy.http import FormRequest
from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
class TrustSxxtSpider(scrapy.Spider):
    name = "trust58_ljzitc_spider"
    allowed_domains = ["ljzitc.com.cn"]

    start_urls = (
        'http://www.ljzitc.com.cn/news/cpjz/index.html',
    )


    def parse(self, response):
        self.log(response.url)
        # html = get_requests(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all("tr")
        for tr in trs:
            tds=tr.find_all("td")
            if len(tds)==3:
                url = "http://www.ljzitc.com.cn"+tds[0].a["href"]
                yield scrapy.Request(url, callback=self.parse_history_nav)



    def parse_history_nav(self, response):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        # html = get_requests(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td',{"class":"tableProcContent"})
            if len(tds)==2:
                item = FundSpiderItem()
                item['fund_full_name'] = soup.title.text.encode("ISO-8859-1")
                item['fund_name'] = soup.title.text.encode("ISO-8859-1")
                item['nav'] = tds[1].text.strip()
                item['statistic_date'] = tds[0].text.strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0058"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item