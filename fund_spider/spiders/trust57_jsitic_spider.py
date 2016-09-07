# -*- coding: utf-8 -*-
"""
陆家嘴信托
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import hashlib
from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime
class TrustSxxtSpider(scrapy.Spider):
    name = "trust57_spider"
    allowed_domains = ["jsitic.net"]

    start_urls = (
        'http://www.jsitic.net/12.html',
    )


    def parse(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all("div", {"class": "float_left hand text-left"})
        for tr in trs[0:3]:
            urll="http://www.jsitic.net"+tr["onclick"].replace("window.location.href=", "").replace("'", "")
            yield scrapy.Request(urll, callback=self.parse_history_nav)


    def parse_history_nav(self, response):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('div', style="height:30px;")
        for tr in trs:
            tds = tr.find_all("div")
            if len(tds) == 4:
                item = FundSpiderItem()
                item['fund_full_name'] = tds[0].text.strip()
                item['fund_name'] = tds[0].text.strip().replace("集合资金信托计划","").replace("江苏信托—","")
                item['nav'] = tds[2].text.strip()
                item['statistic_date'] = tds[1].text.strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0057"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item