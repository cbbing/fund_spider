# -*- coding: utf-8 -*-
"""
甘肃信托
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import re
import hashlib
from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime
class TrustSxxtSpider(scrapy.Spider):
    name = "trust46_spider"
    allowed_domains = ["gstrust.com.cn"]

    start_urls = (
        'http://www.gstrust.com.cn/index.php?m=Article&a=index&id=7',
    )


    def parse(self, response):
        self.log(response.url)
        #请求第一页
        yield scrapy.Request(response.url, callback=self.parse_two, dont_filter=True)
        soup = BeautifulSoup(response.body, "lxml")
        t = soup.find("div", {"class": "pagebar"}).find_all("a")
        tt = t[len(t) - 1]['href'].encode("ISO-8859-1")
        s = re.search("&p=(.*?)$", tt)
        total_page=s.group(1)
        for page in range(2,int(total_page)+1):
            urll="http://www.gstrust.com.cn/index.php?m=Article&a=index&id=7&p=%d"%page
            yield scrapy.Request(urll, callback=self.parse_two)

    def parse_two(self,response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        t = soup.find("div", {"class": "InfoList"}).find_all("div")
        for i in t:
            urll=i.a['href'].replace("", "")

            yield scrapy.Request(urll, callback=self.parse_history_nav)


    def parse_history_nav(self, response):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        item = FundSpiderItem()
        soup = BeautifulSoup(response.body, "lxml")

        t = soup.find("div", {"class": "detailTitle"})
        tt = soup.find_all("span", style="font-family:SimSun;font-size:16px;")
        if t:
            if tt:
                item['fund_name']=t.text.strip().replace("信托单位净值公告", "")
                item['fund_full_name']=t.text.strip().replace("信托单位净值公告", "")
                x = ""
                for i in tt:
                    x = x + i.text.strip()
                s = re.search(u"估值日(.*?)\,\W+人民币(.*?)\。", x)
                ss1=s.group(1).replace("年", "-").replace("月", "-").replace("日", "")
                ss2=s.group(2).replace("元", "")
                if len(ss1)==18:
                    item['statistic_date'] =ss1[0:4] + "-" + ss1[9:11] + "-" + ss1[14:16]
                elif len(ss1)==16:
                    item['statistic_date'] =ss1[0:4] + "-" + ss1[9:10] + "-" + ss1[13:15]
                else:
                    item['statistic_date'] =s.group(1).replace("年", "-").replace("月", "-").replace("日", "")
                if len(ss2)!=6:
                    item['nav'] =ss2[0:6]
                else:
                    item['nav'] =ss2

                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0046"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item