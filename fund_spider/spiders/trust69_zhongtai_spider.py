# -*- coding: utf-8 -*-
"""
中泰信托
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
from util.date_convert import GetNowTime
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
class TrustSxxtSpider(scrapy.Spider):
    name = "trust69_spider"
    allowed_domains = ["zhongtaitrust.com"]

    start_urls = (
        'http://www.zhongtaitrust.com/cn/fortune/products/jinzhi.jsp',
    )


    def parse(self, response):
        self.log(response.url)
        # html = requests.get(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all("td", colspan="3")
        tt = trs[1].find("tr").find("td")["class"]
        ts = filter(str.isdigit, tt[0])
        for i in range(1,int(ts)):
            url = "http://www.zhongtaitrust.com/cn/fortune/products/jinzhi.jsp?pageIndex=%d"%i
            yield scrapy.Request(url, callback=self.parse_history_nav)



    def parse_history_nav(self, response):
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
            tt = tr.find("td", height="50")
            ttt = tr.find("td", {"class": "f11"})
            tttt = tr.find("td", {"class": "tdStatus"})
            if tt is not None:
                item = FundSpiderItem()
                item['fund_name'] = tt.text.strip()
                item['fund_full_name'] = item['fund_name']
                item['nav'] = ttt.text.strip()
                item['foundation_date'] = tttt.text.strip()
                item['statistic_date'] = tttt.text.strip()

                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0069"

                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item