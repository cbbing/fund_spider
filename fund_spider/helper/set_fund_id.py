#coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

"""
设置fund_id
"""
import pandas as pd
from sqlalchemy import create_engine
import fund_spider.settings as settings
engine = create_engine(
    'mysql+mysqldb://{}:{}@{}:3306/{}'.format(settings.MYSQL_USER, settings.MYSQL_PASSWD, settings.MYSQL_HOST,
                                              settings.MYSQL_DBNAME),connect_args={'charset': 'utf8'})


def set_fund_id(org_id):
    table = "classifier_db.t_fund_nv_data"
    sql = "select distinct fund_name from {} where org_id='{}' order by foundation_date asc, entry_time asc".format(table, org_id)
    df = pd.read_sql(sql, engine)

    # 根据基金名称生成fund_id
    name_id_dict = {}
    for ix, row in df.iterrows():
        index = '0' + str(ix+1) if ix < 10 else str(ix+1)
        name_id_dict[row['fund_name']] =  org_id + "XT" + index  #"TG001XT01"
        print row['fund_name'], name_id_dict[row['fund_name']]

    # 设置fund_id
    for ix, row in df.iterrows():
        sql_update = "update {} set fund_id='{}' where fund_name='{}'".format(table, name_id_dict[row['fund_name']], row['fund_name'])
        print sql_update
        engine.execute(sql_update)

if __name__ == "__main__":
    set_fund_id('TG0007')




