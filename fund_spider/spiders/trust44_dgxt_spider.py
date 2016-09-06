# -*- coding: utf-8 -*-
"""
东莞信托
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import re
import hashlib
from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime
import time
class TrustSxxtSpider(scrapy.Spider):
    name = "trust44_spider"
    allowed_domains = ["dgxt.com"]

    start_urls = (
        'http://www.dgxt.com/xthxxlt/index.html',
    )


    def parse(self, response):
        self.log(response.url)
        # 请求第一页
        yield scrapy.Request(response.url, callback=self.parse_two, dont_filter=True)
        soup = BeautifulSoup(response.body, "lxml")
        lis = soup.find("div", {"class": "pages"}).find_all("a")
        t = len(lis)
        total_page=lis[t-2].text
        for page in range(2,int(total_page)+1):
            url = "http://www.dgxt.com/xthxxlt/index_%d.html"%page
            yield scrapy.Request(url, callback=self.parse_two)

    def parse_two(self,response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        lis = soup.find("ul", {"class": "newsdlist274"}).find_all("li")
        for i in lis:
            ts = i.find_all("a")
            if ts:
                urll="http://www.dgxt.com"+ts[1]['href']
                yield scrapy.Request(urll, callback=self.parse_three)


    def parse_three(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        t = soup.find("div", {"class": "pages"}).find_all("a")
        page = t[len(t) - 2].text
        if soup.find("a", {"class": "next"}):
            urll = response.url+"&pageNo=%d" % int(page)
            yield scrapy.Request(urll, callback=self.parse_three)


        else:
            total_page=page
            for pages in range(1,int(total_page)+1):
                urll = response.url + "&pageNo=%d" % int(pages)
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
        lis= soup.find('ul',{"class":"list_poi"}).find_all("li")

        for li in lis:
            tds = li.find_all('div')
            item = FundSpiderItem()
            item['fund_name'] =soup.find("div",{"class":"uynb"}).text
            item['fund_full_name'] =item['fund_name']
            item['nav'] = tds[2].text.strip()
            item['added_nav'] = tds[3].text.strip()
            item['statistic_date'] = tds[1].text.strip()
            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = "TG0044"
            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item