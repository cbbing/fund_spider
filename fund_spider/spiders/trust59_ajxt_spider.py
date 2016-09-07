# -*- coding: utf-8 -*-
"""
爱建信托
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
    name = "trust59_spider"
    allowed_domains = ["ajxt.com.cn"]

    start_urls = (
        'http://www.ajxt.com.cn/Channel/3755',
    )


    def parse(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find('div', {"class": "page"}).find_all("a")
        t = trs[8]['href']
        ts = filter(str.isdigit, t)
        for i in range(1,int(ts)+1):
            url = "http://www.ajxt.com.cn/Channel/3755?_tp_ptpro=%d"%i
            yield scrapy.Request(url, callback=self.parse_history_nav)



    def parse_history_nav(self, response):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds)==3:
                item = FundSpiderItem()
                if "2015" in tds[1].text.strip():
                    item['statistic_date'] = tds[1].text.strip()
                    item['nav'] = tds[2].text.strip()
                elif "2016" in tds[1].text.strip():
                    item['statistic_date'] = tds[1].text.strip()
                    item['nav'] = tds[2].text.strip()
                else:
                    item['nav'] = tds[1].text.strip()
                if tds[2].text.strip() is None:
                    item['statistic_date'] = None
                else:
                    item['statistic_date'] =tds[2].text.strip()
                item['fund_name'] = tds[0].text.strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0059"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item