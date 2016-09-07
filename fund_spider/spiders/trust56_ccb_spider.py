# -*- coding: utf-8 -*-
"""
建信信托
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
    name = "trust56_spider"
    allowed_domains = ["ccbtrust.com.cn"]

    start_urls = (
        'http://www.ccbtrust.com.cn/templates/second/index.aspx?nodeid=16',
    )


    def parse(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find('span', {"class": "page"})
        t = trs.text.strip()
        tt = re.compile(r"\d+")
        page_totle=tt.findall(t)[0]
        for page in range(1,int(page_totle)+1):
            url='http://www.ccbtrust.com.cn/templates/second/index.aspx?nodeid=16&pagesize=%d&pagenum=10'%page
            yield scrapy.Request(url, callback=self.parse_two)


    def parse_two(self,response):
        self.log(response.url)
        # 请求第一页
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('ul', {"class": "ArticleList"})
        for tr in trs:
            lis = tr.find_all("li")
            if len(lis) == 2:
                url = lis[0].a['href']
                yield scrapy.Request(url,callback=self.parse_history_nav)

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
            ps = tr.find_all('p')
            if len(ps)==3:
                if "产品名称" == ps[0].font.text:
                    continue
                item = FundSpiderItem()
                item['fund_full_name'] = ps[0].font.text.strip()
                item['fund_name'] = ps[0].font.text.strip()
                item['statistic_date'] = ps[1].font.text.strip()
                item['nav'] = ps[2].font.text.strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0056"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item