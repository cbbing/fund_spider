# -*- coding: utf-8 -*-
"""
方正信托
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
class TrustSxxtSpider(scrapy.Spider):
    name = "trust45_spider"
    allowed_domains = ["fd-trust.com"]

    start_urls = (
        'http://www.fd-trust.com/index/show/tid/47.html',
    )


    def parse(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        t = soup.find("td", align="center")
        tt = t.text
        s = re.search(u"\/(.*?)页", tt)
        total_page=s.group(1)
        for page in range(1,int(total_page)+1):
            url = "http://www.fd-trust.com/home/index/show/tid/47/p/%d.html"%page
            yield scrapy.Request(url, callback=self.parse_two)

    def parse_two(self,response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        lis = soup.find("ul", {"class": "pro_ul"}).find_all("li")
        for i in lis:
            urll="http://www.fd-trust.com" + i.a['href']
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
            if tds[0].p:
                if tds[0].p.text.strip()!= "估值日" and tds[0].p.text.strip()!= "估值时间":
                    item = FundSpiderItem()
                    if tds[0].p:
                        item['statistic_date'] = tds[0].p.text.strip()
                    else:
                        item['statistic_date'] = tds[0].text.strip()
                    if tds[1].p:
                        item['nav'] = tds[1].p.text.strip()
                    else:
                        item['nav'] = tds[1].text.strip()
                    item['fund_name'] = soup.find("h3").text
                    item['fund_full_name'] = item['fund_name']
                    item['entry_time'] = GetNowTime()
                    item['source_code'] = 1
                    item['source'] = response.url
                    item['org_id'] = "TG0045"
                    item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                    print item
                    yield item
            else:
                item = FundSpiderItem()
                if tds[0].p:
                    item['statistic_date'] = tds[0].p.text.strip()
                else:
                    item['statistic_date'] = tds[0].text.strip()
                if tds[1].p:
                    item['nav'] = tds[1].p.text.strip()
                else:
                    item['nav'] = tds[1].text.strip()
                item['fund_name'] = soup.find("h3").text
                item['fund_full_name'] = item['fund_name']
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0045"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item

            # if len(tds)==2 and tds[0].p.text.strip()!="估值日":
            #     item = FundSpiderItem()
            #     item['fund_name'] =soup.find("h3").text
            #     item['fund_full_name'] =item['fund_name']
            #     item['nav'] = tds[1].p.text.strip()
            #     item['statistic_date'] = tds[0].p.text.strip()
            #     item['entry_time'] = GetNowTime()
            #     item['source_code'] = 1
            #     item['source'] = response.url
            #     item['org_id'] = "TG0045"
            #     item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            #     print item
            #     yield item