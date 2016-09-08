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
        'http://www.ccbtrust.com.cn/templates/second/index.aspx?nodeid=16&pagesize=1&pagenum=100',
    )


    def parse(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find('span', {"class": "page"})
        t = trs.text.strip()
        tt = re.compile(r"\d+")
        page_totle=tt.findall(t)[0]
        for page in range(1,int(page_totle)+1):
            url='http://www.ccbtrust.com.cn/templates/second/index.aspx?nodeid=16&pagesize=%d&pagenum=100'%page
            yield scrapy.Request(url, callback=self.parse_two, dont_filter=True)



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

        isDateStart = False
        title = ''

        for tr in trs:
            tds = tr.find_all('td')
            if len(tds)==5:
                # http://www.ccbtrust.com.cn/templates/second/index.aspx?nodeid=16&page=ContentPage&contentid=9084
                if "产品名称" == tds[0].text.strip():
                    continue
                item = FundSpiderItem()
                item['fund_name'] = tds[0].text.strip()
                item['fund_full_name'] = item['fund_name']
                if '成立日' in tds[1].text:
                    print tds[1].text
                item['statistic_date'] = tds[1].text.replace('成立日','').replace("(",'').replace(")","") \
                    .replace("（", '').replace("）", "")                                    \
                    .strip()
                item['nav'] = tds[2].text.strip()

                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0056"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item
            elif len(tds) == 3:
                if "日期" == tds[0].text.strip():
                    isDateStart = True
                    title = soup.find('h2').text.replace("计划收益",'')
                    continue
                item = FundSpiderItem()
                if isDateStart:
                    # http://www.ccbtrust.com.cn/templates/second/index.aspx?nodeid=16&page=ContentPage&contentid=9074
                    item['fund_name'] = title
                    item['fund_full_name'] = item['fund_name']
                    item['statistic_date'] = tds[0].text
                    item['nav'] = tds[1].text.strip()
                else:
                    # http://www.ccbtrust.com.cn/templates/second/index.aspx?nodeid=16&page=ContentPage&contentid=9075
                    item['fund_name'] = tds[0].text.strip()
                    item['fund_full_name'] = item['fund_name']
                    item['statistic_date'] = tds[1].text
                    item['nav'] = tds[2].text.strip()

                item['statistic_date'] = item['statistic_date'].replace('成立日', '').replace("(", '').replace(")", "") \
                    .replace("（", '').replace("）", "").strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0056"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item