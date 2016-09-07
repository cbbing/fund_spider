# -*- coding: utf-8 -*-
"""
金谷信托
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
    name = "trust65_spider"
    allowed_domains = ["jingutrust.com"]

    start_urls = (
        'http://www.jingutrust.com/jgxt/common/informationsProductVal.jsp',
    )


    def parse(self, response):
        self.log(response.url)

        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('li',{"class":"product_li_1"})
        x=1
        for tr in trs:
            url=tr.find("a")["href"]
            if url:
                trs=tr.find_all("div")
                item = FundSpiderItem()
                item['fund_name'] = tr.find("a").text.strip()
                item['fund_full_name'] = tr.find("a").text.strip()
                item['foundation_date'] = trs[2].text.strip()
                yield scrapy.Request(url, callback=lambda response, item=item : self.parse_history_nav(response, item))



    def parse_history_nav(self, response,fistitem):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")

        trs = soup.find_all('li')
        for tr in trs:
            tds = tr.find_all('div')
            if len(tds)==3:
                item = FundSpiderItem()
                item['fund_name'] = fistitem['fund_name']
                item['fund_full_name'] = fistitem['fund_full_name']
                item['foundation_date'] = fistitem['foundation_date']
                item['statistic_date'] = tds[0].text.strip()
                item['nav'] = tds[1].text.strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0065"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item