# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FundSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    uuid = scrapy.Field()
    fund_id = scrapy.Field()  #自己添加
    fund_code = scrapy.Field() #平台自带
    fund_name = scrapy.Field()
    fund_full_name = scrapy.Field()
    open_date = scrapy.Field()
    nav = scrapy.Field()
    added_nav  = scrapy.Field()
    foundation_date = scrapy.Field()
    statistic_date = scrapy.Field()
    entry_time = scrapy.Field()
    source_code = scrapy.Field()
    source = scrapy.Field()
    org_id = scrapy.Field()

    # def __unicode__(self):
    #     return self.fund_name+","+self.foundation_date
    def __str__(self):
        values = ''
        for key in self.iterkeys():
            values += "{}:{}\n".format(key, self[key])
        return values

class FundNvDataItem(scrapy.Item):
    # define the fields for your item here like:
    uuid = scrapy.Field()
    fund_id = scrapy.Field()  # 自己添加
    fund_name = scrapy.Field()
    fund_full_name = scrapy.Field()
    reg_code = scrapy.Field()
    nav = scrapy.Field()
    swanav = scrapy.Field()
    sanav = scrapy.Field()
    statistic_date = scrapy.Field()
    entry_time = scrapy.Field()
    source_code = scrapy.Field()
    data_source = scrapy.Field()
    data_source_name = scrapy.Field()

    def __str__(self):
        values = ''
        for key in self.iterkeys():
            values += "{}:{}\n".format(key, self[key])
        return values

class FundSecurityDataItem(scrapy.Item):
    fund_id=scrapy.Field()
    fund_name=scrapy.Field()
    statistic_datel=scrapy.Field()
    stock_id=scrapy.Field()
    stock_name=scrapy.Field()
    stock_sum=scrapy.Field()
    stock_ratio=scrapy.Field()
    data_source=scrapy.Field()
    data_source_name=scrapy.Field()
    entry_time=scrapy.Field()

    def __str__(self):
        values = ''
        for key in self.iterkeys():
            values += "{}:{}\n".format(key, self[key])
        return values


class FundAllocationItem(scrapy.Item):
    fund_id = scrapy.Field()
    fund_name = scrapy.Field()
    fund_allocation_category=scrapy.Field()
    statistic_date2=scrapy.Field()
    split_ratio=scrapy.Field()
    after_tax_bonus=scrapy.Field()
    data_source = scrapy.Field()
    data_source_name = scrapy.Field()
    entry_time = scrapy.Field()

    def __str__(self):
        values = ''
        for key in self.iterkeys():
            values += "{}:{}\n".format(key, self[key])
        return values

class FundInfoItem(scrapy.Item):
    uuid = scrapy.Field()
    fund_id = scrapy.Field()  # 自己添加
    fund_name = scrapy.Field()
    fund_full_name = scrapy.Field()
    reg_code = scrapy.Field()
    fund_status = scrapy.Field()
    fund_member = scrapy.Field()
    locked_time_limit = scrapy.Field()
    open_date = scrapy.Field()
    min_purchase_amount = scrapy.Field()
    min_append_amount = scrapy.Field()
    fee_subscription = scrapy.Field()
    fee_redeem = scrapy.Field()
    precautious_line = scrapy.Field()
    stop_loss_line = scrapy.Field()
    fund_manager = scrapy.Field()
    fee_pay = scrapy.Field()
    fund_manager_nominal = scrapy.Field()
    fee_manage = scrapy.Field()
    fund_custodian = scrapy.Field()
    fund_stockbroker = scrapy.Field()
    foundation_date=scrapy.Field()
    init_total_asset = scrapy.Field()
    duration = scrapy.Field()
    fund_type_structure = scrapy.Field()
    is_umbrella_fund = scrapy.Field()
    fund_type_issuance = scrapy.Field()
    typestandard_name = scrapy.Field()
    type_name = scrapy.Field()
    stype_name = scrapy.Field()
    data_source=scrapy.Field()
    data_source_name=scrapy.Field()
    entry_time=scrapy.Field()
    data_freq = scrapy.Field()

    fee_pay_remark = scrapy.Field()
    redeem_limit = scrapy.Field()
    redeem_data_remark = scrapy.Field()
    redeem_account_remark = scrapy.Field()

    def __str__(self):
        values = ''
        for key in self.iterkeys():
            values += "{}:{}\n".format(key, self[key])
        return values

class FundPersonItem(scrapy.Item):
    uuid = scrapy.Field()
    user_id=scrapy.Field()
    user_name=scrapy.Field()
    org_name=scrapy.Field()
    duty=scrapy.Field()
    background=scrapy.Field()
    investment_years=scrapy.Field()
    eduction=scrapy.Field()
    resume=scrapy.Field()
    remark=scrapy.Field()
    data_source = scrapy.Field()
    data_source_name = scrapy.Field()
    entry_time = scrapy.Field()
    graduateschool=scrapy.Field()
    org_name_before=scrapy.Field()

    fund_id = scrapy.Field()

    def __str__(self):
        values = ''
        for key in self.iterkeys():
            values += "{}:{}\n".format(key, self[key])
        return values

class FundOrgItem(scrapy.Item):
    uuid = scrapy.Field()
    org_id=scrapy.Field()
    org_name=scrapy.Field()
    org_full_name = scrapy.Field()
    core_member=scrapy.Field()
    fund_date=scrapy.Field()
    reg_date=scrapy.Field()
    area=scrapy.Field()
    manage_fund_number=scrapy.Field()
    profile=scrapy.Field()
    team=scrapy.Field()
    investment_idea=scrapy.Field()
    reg_capital=scrapy.Field()
    prize=scrapy.Field()
    ridk_management=scrapy.Field()
    data_source = scrapy.Field()
    data_source_name = scrapy.Field()
    entry_time = scrapy.Field()
    remark = scrapy.Field()

    def __str__(self):
        values = ''
        for key in self.iterkeys():
            values += "{}:{}\n".format(key, self[key])
        return values
