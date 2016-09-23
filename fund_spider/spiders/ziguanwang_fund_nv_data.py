# -*- coding: utf-8 -*-
"""

"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import hashlib
import datetime
from selenium import webdriver  #导入包
from fund_spider.items import FundNvDataItem
from scrapy.http import  FormRequest
import requests,json
from util.date_convert import GetNowTime
class TrustSxxtSpider(scrapy.Spider):
    name = "ziguan_spider"
    allowed_domains = ["ziguan123.com"]

    start_urls = (
        'http://www.ziguan123.com/ajax/productrank',
    )
    # def start_requests(self):
    #     url="http://www.ziguan123.com/ajax/productrank"
    #     requests=[]
    #     formdata = {  # 表单
    #         "operator_type": "27",
    #         "policyfirstlevel": "89,90,91,92,93",
    #         "policy": "0",
    #         "fundtype": "",
    #         "terms": "1",
    #         "sermonth": "2016-08",
    #         "sort_name": "Month1",
    #         "sort_type": "desc",
    #         "page_index": "1",
    #         "page_size": "40"
    #     }
    #     request=FormRequest(url,callable=self.parse,formdata=formdata)
    #     requests.append(request)
    #     return  requests

    def parse(self, response):
        self.log(response.url)
        data = {  # 表单
            "operator_type": "27",
            "policyfirstlevel": "89,90,91,92,93",
            "policy": "0",
            "fundtype": "",
            "terms": "1",
            "sermonth": "2016-08",
            "sort_name": "Month1",
            "sort_type": "desc",
            "page_index": "1",
            "page_size": "40"
        }
        t = requests.post(response.url, data=data)  # 向服务器发送post请求
        soup = BeautifulSoup(t.text, "lxml")
        t = json.loads(soup.text)
        #li = t['rawdata']['data']
        pages = t['rawdata']['data'][0]['operator_type']
        for i in range(1, int(pages) + 1):
            data = {  # 表单
                "operator_type": pages,
                "policyfirstlevel": "89,90,91,92,93",
                "policy": "0",
                "fundtype": "",
                "terms": "1",
                "sermonth": "2016-08",
                "sort_name": "Month1",
                "sort_type": "desc",
                "page_index": i,
                "page_size": "40"
            }
            #url = "http://www.ziguan123.com/ajax/productrank"  # 在F12里面找的json
            t = requests.post(response.url, data=data)  # 向服务器发送post请求
            soup = BeautifulSoup(t.text, "html5lib")
            t = json.loads(soup.text)
            li = t['rawdata']['data']
            print "--------------------page%d------------" % i
            count = 0
            for i in li:

                #print "http://www.ziguan123.com/product/detail/" + i['id']
                url = "http://www.ziguan123.com/product/detail/" + i['id']
                header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"}
                try:
                    t = requests.get("http://www.ziguan123.com/product/detail/" + i['id'], header)
                    requests.adapters.DEFAULT_RETRIES = 5
                    soup = BeautifulSoup(t.text, "html5lib")
                    t.close()
                    trs = soup.find_all("td", align="left")
                except:
                    while count <= 6:
                        try:
                            t = requests.get("http://www.ziguan123.com/product/detail/" + i['id'], header)
                            requests.adapters.DEFAULT_RETRIES = 5
                            soup = BeautifulSoup(t.text, "html5lib")
                            t.close()
                            trs = soup.find_all("td", align="left")
                            break
                        except:
                            count = count + 1
                if len(trs)>0:
                    for tr in trs:
                        #print tr.a['href'] + "\t" + tr.a.text
                        urll="http://www.ziguan123.com"+tr.a['href']
                        yield scrapy.Request(urll, callback=self.parse_two)


                else:
                    yield scrapy.Request(url, callback=self.parse_two)





    def parse_two(self,response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "html5lib")
        title = soup.find("h1", {"class": "cp-title"})
        if title:

            print title.text
            print response.url
            num = response.url.replace("http://www.ziguan123.com/product/detail/", "")
            url = "http://www.ziguan123.com/product/ajaxlinechart"
            data = {  # 表单
                "productid": num,
            }
            t = requests.post(url, data=data)  # 向服务器发送post请求
            soup = BeautifulSoup(t.text, "html5lib")
            #print soup.text
            tt = json.loads(soup.text)
            for i in tt['data']:
                item = FundNvDataItem()
                # 将时间撮换为标准时间
                timeStamp = int(i['valuedate']) / 1000
                dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
                otherStyleTime = dateArray.strftime("%Y-%m-%d")
                #print otherStyleTime + "\t" + i['netunit'] + "\t" + i['totalnet']
                item['fund_name']=title.text
                item['fund_full_name'] = title.text
                item['fund_id'] =num
                item['nav'] = i['netunit']
                item['swanav'] = i['totalnet']
                item['statistic_date'] = otherStyleTime
                item['entry_time'] = GetNowTime()
                item['source_code'] = "3-第三方"
                item['data_source'] = 6
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                # yield scrapy.Request(response.url,
                #                      callback=lambda response, item=item: self.parse_three(response, item))
                print item
                yield item


    # def parse_three(self,response):
    #     self.log(response.url)
    #     item=d_fund_info()
    #     soup = BeautifulSoup(response.body, "lxml")
    #     title = soup.find("h1", {"class": "cp-title"})
    #     if title:
    #         print title.text
    #         print response.url
    #         num = response.url.replace("http://www.ziguan123.com/product/detail/", "")
    #     ss = soup.find("li", {"class": "li_onfor_01"})
    #     print ss.text.split()[1]
    #     t = ss.text.split()[1]
    #     fund_status = t.replace("运行状态：", "")
    #     item['fund_id']=num
    #     item['fund_name']=title.text
    #     item['fund_full_name']=title.text
    #     item['fund_status']=fund_status
    #     rs = soup.find("table", {"class": "tablebor_xy table_td_w25p "})
    #     trs = rs.find_all("tr")
    #
    #     tds = trs[1].find_all("td")
    #     # print "投资顾问：" + tds[1].text.strip()
    #     item['fund_manager'] = tds[1].text.strip()
    #     # print "基金经理：" + tds[3].text.strip()
    #     item['fund_member'] =tds[3].text.strip()
    #
    #     tds = trs[2].find_all("td")
    #     # print "基金类型：" + tds[1].text.strip()
    #     item['fund_type_issuance'] = tds[1].text.strip()
    #     # print "成立时间：" + tds[3].text.strip()
    #     item['foundation_date'] = tds[3].text.strip()
    #
    #     tds = trs[3].find_all("td")
    #     # print "受托人：" + tds[1].text.strip()
    #     # print "期限（年）：" + tds[3].text.strip()
    #     item['duration'] = tds[3].text.strip()
    #
    #     tds = trs[4].find_all("td")
    #     # print "证劵经纪人：" + tds[1].text.strip()
    #     item['fund_stockbroker'] = tds[1].text.strip()
    #     # print "托管银行：" + tds[3].text.strip()
    #     item['fund_custodian'] = tds[3].text.strip()
    #
    #     tds = trs[5].find_all("td")
    #     # print "认购门槛：" + tds[1].text.strip()
    #     item['min_purchase_amount'] = tds[1].text.strip()
    #     # print "初始规模：" + tds[3].text.strip()
    #     item['init_total_asset'] = tds[3].text.strip()
    #
    #     tds = trs[6].find_all("td")
    #     # print "封闭期：" + tds[1].text.strip()
    #     item['locked_time_limit'] = tds[1].text.strip()
    #     # print "开放日：" + tds[3].text.strip()
    #     item['open_date'] = tds[3].text.strip()
    #
    #     tds = trs[7].find_all("td")
    #     # print "认购费：" + tds[1].text.strip()
    #     item['fee_subscription'] = tds[1].text.strip()
    #     # print "赎回费：" + tds[3].text.strip()
    #     item['fee_redeem'] = tds[3].text.strip()
    #
    #     tds = trs[8].find_all("td")
    #     # print "管理费：" + tds[1].text.strip()
    #     item['fee_manage'] = tds[1].text.strip()
    #     # print "业绩报酬：" + tds[3].text.strip()
    #     item['fee_pay'] = tds[3].text.strip()
    #
    #     item['type_name']="CTA策略|股票对冲|组合基金|全球宏观|债券策略"
    #     item['entry_time'] = GetNowTime()
    #     item['uuid'] = hashlib.md5((item['fund_name'] + item['foundation_date']).encode('utf8')).hexdigest()
    #     print item
    #     yield item




        #yield scrapy.Request(urls, callback=self.parse_history_nav)



    # def parse_history_nav(self, response):
    #     """
    #     历史净值
    #     :param response:
    #     :param itemTop:
    #     :return:
    #     """
    #     self.log(response.url)
    #     soup = BeautifulSoup(response.body, "html5lib")
    #     trs = soup.find_all('tr')
    #     for tr in trs:
    #         tds = tr.find_all('td',{"class":"tableProcContent"})
    #         if len(tds)==2:
    #             item = FundSpiderItem()
    #             item['fund_full_name'] = soup.title.text
    #             item['fund_name'] = soup.title.text
    #             item['nav'] = tds[1].text.strip()
    #             item['statistic_date'] = tds[0].text.strip()
    #             item['entry_time'] = GetNowTime()
    #             item['source_code'] = 1
    #             item['source'] = response.url
    #             item['org_id'] = "TG0058"
    #             item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
    #             print item
    #             yield item
