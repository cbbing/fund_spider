# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import redis
import pandas as pd
from sqlalchemy import create_engine
import threading

from scrapy.exceptions import DropItem
from items import *
import fund_spider.settings as settings

engine = create_engine('mysql+mysqldb://{}:{}@{}:3306/{}'.format(settings.MYSQL_USER, settings.MYSQL_PASSWD, settings.MYSQL_HOST, settings.MYSQL_DBNAME) ,
                       connect_args={'charset': 'utf8'},
                       pool_size=8)
redis_db4 = redis.Redis(host=settings.REDIS_HOST, port=6379, db=4, password=settings.REDIS_PWD)
redis_fund_dict = "fund_uuids"

mysql_table_trust_nav = "t_fund_nv_data"
mysql_table_ziguan_fund_nav = "d_fund_nv_data"
mysql_table_ziguan_fund_info = "d_fund_info"
mysql_table_ziguan_fund_person = "d_fund_person"
mysql_table_ziguan_fund_org = "d_fund_org"

mutex = threading.Lock()

class DuplicatePipeline(object):
    """
    去重(redis)
    """

    def __init__(self):
        if redis_db4.hlen(redis_fund_dict) == 0:
            sql = "SELECT uuid FROM {}".format(mysql_table_trust_nav)
            df = pd.read_sql(sql, engine)
            for uuid in df['uuid'].get_values():
                redis_db4.hset(redis_fund_dict, uuid, 0)

    def process_item(self, item, spider):

        if type(item) is FundSpiderItem:
            if redis_db4.hexists(redis_fund_dict, item['uuid']):
                raise DropItem("Duplicate item found:%s" % item)

        return item

class ValueVerificationPipeline(object):
    """
    有效性验证
    """
    def process_item(self, item, spider):
        if type(item) == FundSpiderItem:
            if not item['fund_name'] or not item['nav'] or not item['statistic_date']:
                raise DropItem("Missing fund_name or nav or statistic_date in %s" % item)
            elif item['statistic_date']:
                print item['statistic_date']
                dateFind = re.search('\d{4}.*?\d{1,2}.*?\d{1,2}', item['statistic_date'])
                if not dateFind:
                    raise DropItem("statistic_date format not right! in %s" % item)
            elif item['nav']:
                if not item['nav'].replace('.', '').isdigit():
                    raise DropItem('nav is not float format! in %s' % item)

        return item

class SetFundIDPipeline(object):
    """
    设置fund_id字段
    """
    def process_item(self, item, spider):

        if type(item) == FundSpiderItem:

            if mutex.acquire(): # 互斥锁 加锁

                sql = "select distinct fund_id from {} where fund_name='{}' ".format(mysql_table_trust_nav, item['fund_name'])
                df = pd.read_sql(sql, engine)
                fund_ids = df['fund_id'].get_values()
                if len(fund_ids) and fund_ids[0]: # 数据库中存在fund_id, 直接赋值
                    item['fund_id'] = fund_ids[0]
                else:  # 数据库中不存在, 新建一个fund_id
                    sql = "SELECT distinct fund_id FROM {}  where org_id ='{}' order by length(fund_id) desc, fund_id desc".format(
                        mysql_table_trust_nav, item['org_id']
                    )
                    df = pd.read_sql(sql, engine)
                    fund_ids = df['fund_id'].get_values()
                    if len(fund_ids) and fund_ids[0]:
                        find_last_id = re.search("XT(\d+)", fund_ids[0])
                        if find_last_id:
                            last_id = int(find_last_id.group(1))+1
                        index = '0'+str(last_id) if last_id < 10 else str(last_id)
                        new_fund_id = item['org_id'] + "XT" + index
                    else:
                        new_fund_id = item['org_id'] + "XT" + "01"

                    item['fund_id'] = new_fund_id

                mutex.release()  # 互斥锁 释放

        elif type(item) == FundPersonItem:

            if mutex.acquire():  # 互斥锁 加锁

                sql = "select distinct user_id from {} where user_name='{}' ".format(mysql_table_ziguan_fund_person,
                                                                                     item['user_name'])
                df = pd.read_sql(sql, engine)
                user_ids = df['user_id'].get_values()
                if len(user_ids) and user_ids[0]:  # 数据库中存在user_id, 直接赋值
                    item['user_id'] = user_ids[0]
                else:  # 数据库中不存在, 新建一个user_id
                    sql = "SELECT distinct user_id FROM {} where user_id like '%{}%' order by length(user_id) desc, user_id desc".format(
                        mysql_table_ziguan_fund_person, item['user_id']
                    )
                    df = pd.read_sql(sql, engine)
                    user_ids = df['user_id'].get_values()
                    if len(user_ids) and user_ids[0]:
                        find_last_id = re.search("P(\d+)", user_ids[0])
                        if find_last_id:
                            last_id = int(find_last_id.group(1)) + 1
                        new_user_id = item['user_id'] + "P" + str(last_id)
                    else:
                        new_user_id = item['user_id'] + "P" + "1"

                    item['user_id'] = new_user_id

                mutex.release()  # 互斥锁 释放

        elif type(item) == FundOrgItem:

            if mutex.acquire():  # 互斥锁 加锁

                sql = "select distinct org_id from {} where org_full_name='{}' ".format(mysql_table_ziguan_fund_org,
                                                                                     item['org_full_name'])
                df = pd.read_sql(sql, engine)
                org_ids = df['org_id'].get_values()
                if len(org_ids) and org_ids[0]:  # 数据库中存在org_id, 直接赋值
                    item['org_id'] = org_ids[0]
                else:  # 数据库中不存在, 新建一个org_id
                    sql = "SELECT distinct org_id FROM {} where org_id like '%{}%' order by length(org_id) desc, org_id desc".format(
                        mysql_table_ziguan_fund_org, item['org_id']
                    )
                    df = pd.read_sql(sql, engine)
                    org_ids = df['org_id'].get_values()
                    if len(org_ids) and org_ids[0]:
                        find_last_id = re.search("O(\d+)", org_ids[0])
                        if find_last_id:
                            last_id = int(find_last_id.group(1)) + 1
                            new_user_id = item['org_id'] + "O" + str(last_id)
                    else:
                        new_user_id = item['org_id'] + "O" + "1"

                    item['org_id'] = new_user_id

                mutex.release()  # 互斥锁 释放

        return item


class MySQLStorePipeline(object):

    def __init__(self):
        self.fund_items = {}

    def process_item(self, item, spider):

        # self.fund_items.setdefault(spider.name, [])
        # self.fund_items[spider.name].append(item)

        table_dict = {FundSpiderItem : mysql_table_trust_nav,
                      FundNvDataItem : mysql_table_ziguan_fund_nav,
                      FundInfoItem : mysql_table_ziguan_fund_info,
                      FundPersonItem : mysql_table_ziguan_fund_person,
                      FundOrgItem : mysql_table_ziguan_fund_org}
        table = table_dict.get(type(item))

        df = pd.DataFrame([item])
        print df
        try:
            df.to_sql(table, engine, if_exists='append', index=False)
            # redis_db4.hset(redis_fund_dict, item['uuid'], item['org_id'])
        except Exception,e:
            raise DropItem('insert to mysql error! %s, %s' % (item, e))

        return item

    def close_spider(self, spider):
        pass
