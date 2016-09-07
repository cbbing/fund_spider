# -*- coding: utf-8 -*-
"""
国民信托
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import re,json
import hashlib
from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime
class TrustSxxtSpider(scrapy.Spider):
    name = "trust48_spider"
    allowed_domains = ["natrust.cn"]

    start_urls = (
        'http://www.natrust.cn/fe/equity/catList.gsp?rd=0.7051245598957054',
    )


    def parse(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        uls = soup.find_all('ul', {"class":"job_list_text job_list_text2"})
        for ul in uls:
            lis=ul.find_all("li")
            if len(lis)==5:
                urll="http://www.natrust.cn/fe/equity/"+lis[0].a['href']
                yield scrapy.Request(urll, callback=self.parse_two)

    def parse_two(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        t = soup.find("form", {"name": "eform"})
        tt = t.text.strip()
        t = re.compile(r"\d+")
        totle_page=t.findall(tt)[1]
        for page in range(1,int(totle_page)+1):
            urll=response.url+"&page={}".format(page)
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
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) == 4 and tds[0].text.strip() != "日期":
                item = FundSpiderItem()
                item['fund_name'] =soup.find("div",{"class":"left"}).text.strip().replace("国民信托·","")\
                                    .replace("证券投资集合资金信托计划","").replace("集合资金信托计划","")
                item['fund_full_name'] = soup.find("div",{"class":"left"}).text.strip()
                item['nav'] = tds[1].text.strip()
                item['added_nav']=tds[2].text.strip()
                item['statistic_date'] = tds[0].text.strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0048"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item