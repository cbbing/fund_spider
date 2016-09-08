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
    name = "trust58_spider"
    allowed_domains = ["ljzitc.com.cn"]

    # start_urls = (
    #     'http://www.ljzitc.com.cn/news/cpjz/index.html',
    # )

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Cookie": "Hm_lvt_28e102dd14491ddb45aedf4e66d575e4=1472521033,1473304336; Hm_lpvt_28e102dd14491ddb45aedf4e66d575e4=1473313968",
        "Host": "www.ljzitc.com.cn",
        "If-Modified-Since": "Tue, 06 Sep 2016 08:35:34 GMT",
        "If-None-Match": "83fcc9a2198d21:0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }

    def start_requests(self):
        return [scrapy.Request(url='http://www.ljzitc.com.cn/news/cpjz/index.html', headers=self.headers)]


    def parse(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all("tr")
        for tr in trs:
            tds=tr.find_all("td")
            if len(tds)==3:
                url = "http://www.ljzitc.com.cn"+tds[0].a["href"]
                yield scrapy.Request(url, headers=self.headers, callback=self.parse_history_nav)



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