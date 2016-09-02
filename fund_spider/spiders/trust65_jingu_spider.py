# -*- coding: utf-8 -*-
"""
金谷信托
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
    name = "trust65_spider"
    allowed_domains = ["jingutrust.com"]

    start_urls = (
        'http://www.jingutrust.com/jgxt/common/informationsProductVal.jsp',
    )


    def parse(self, response):
        self.log(response.url)

        # html = requests.get(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('li',{"class":"product_li_1"})
        # x=1
        for tr in trs:
            url=tr.find("a")["href"]
            if url:
                trs=tr.find_all("div")
                item = FundSpiderItem()
                item['fund_name'] = tr.find("a").text.strip()
                item['fund_full_name'] = tr.find("a").text.strip()
                item['foundation_date'] = trs[2].text.strip()
                yield scrapy.Request(url, callback=lambda response, item=item : self.parse_history_nav(response, item))

    # def parse_two(self,response,Fistitem):
    #     self.log(response.url)
    #     # 请求第一页
    #     item = FundSpiderItem()
    #     item['fund_name'] = Fistitem['fund_name']
    #     item['fund_full_name'] = Fistitem['fund_full_name']
    #     item['foundation_date'] = Fistitem['foundation_date']
    #     item['statistic_date'] = Fistitem['statistic_date']
    #     html = requests.get(response.url)
    #     soup = BeautifulSoup(html.text, "lxml")
    #     trs = soup.find_all('td')
    #     for tr in trs:
    #         urls = tr.find("div")
    #         if urls:
    #             urll= "http://www.msxt.com" + urls.a['href']
    #
    #             item['foundation_date'] = tr.next_sibling.next_sibling.text
    #             item['open_date']=tr.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.text
    #             # print item
    #             # yield item
    #             yield scrapy.Request(urll, callback=lambda response, item=item : self.parse_history_nav(response, item))
    #


    def parse_history_nav(self, response,Fistitem):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        # html = requests.get(response.url)
        soup = BeautifulSoup(response.body, "lxml")

        trs = soup.find_all('li')
        for tr in trs:
            tds = tr.find_all('div')
            if len(tds)==3:
                item = FundSpiderItem()
                item['fund_name'] = Fistitem['fund_name']
                item['fund_full_name'] = Fistitem['fund_full_name']
                item['foundation_date'] = Fistitem['foundation_date']
                item['statistic_date'] = tds[0].text.strip()
                item['nav'] = tds[1].text.strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0065"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item