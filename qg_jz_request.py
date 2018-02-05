# coding=utf-8
import requests
from lxml import etree
import time
import re
from zhixing import ZhixingSpider
from shixin import ShixinSpider
from rand_ua import Rand_ua
from cpws import Cp_spider
import pymongo

# 改进方向
# 使用无头浏览器代替Chome 提高请求速度
# 捕捉各个模块的异常并计入日志
# 增加断点需爬功能
# 增加去重功能
# 使用多线程


class Qg_jz(object):

    def __init__(self):
        u = Rand_ua()
        ua = u.rand_chose()
        self.headers = {'User-Agent': '{}'.format(ua)}
        self.company_type = 3
        self.company_total = 30
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.conn = self.client["qg_text"]['company']

    def start_requests(self, page):
        url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
        item = {}
        item["page"] = str(page)
        post_data = {
                "data - target": "_blank",
                "$total": "{}".format(self.company_total),
                "$rekoad": "0",
                "qy_type": "QY_ZZ_ZZZD_00{}".format(self.company_type),
                "$pg": str(page),
                "class": "formsubmit activeTinyTab",
                "data - url": "/ dataservice / query / comp / list",
                "$pgsz": "15"}
        ret = requests.post(url, data=post_data, headers=self.headers)
        html = ret.content.decode()

        response = etree.HTML(html)
        return response, item

    # 提取列表信息
    def get_list(self, response, item):
        tr_list = response.xpath("//tbody[@class='cursorDefault']//tr")
        for tr in tr_list:
            company = tr.xpath('.//td[@data-header="企业名称"]/a/text()')[0].strip()
            item["company"] = company if company else ""
            detail_href = tr.xpath('.//td[@data-header="企业名称"]/a/@href')[0].strip()
            if len(detail_href) > 0:
                # http://jzsc.mohurd.gov.cn/dataservice/query/comp/caDetailList/001607220057249990?_=1517366694950
                item["_id"] = re.findall(r'/dataservice/query/comp/compDetail/(\d+)', detail_href)[0]
                nd = int(time.time())*1000
                cf_href = "http://jzsc.mohurd.gov.cn/dataservice/query/comp/caDetailList/{}?_={}".format(item["_id"], nd)
                ret = requests.get(cf_href)
                response = etree.HTML(ret.content.decode())
                data = self.cf_parse(response, item)
                self.save_mongodb(data)
                print(data)

    # 提取资质信息
    def cf_parse(self, response, item):
        item["data"] = []
        cf_item = {}
        tr_list = response.xpath("//tbody[@class='cursorDefault']//tr")
        cf_item["资质信息"] = []
        for tr in tr_list:
            cf_one = []
            cf_type = tr.xpath(".//td[@data-header='资质类别']/text()")
            cf_type = cf_type[0].strip() if cf_type else ""
            cf_id = tr.xpath(".//td[@data-header='资质证书号']/text()")
            cf_id = cf_id[0].strip() if cf_id else ""
            cf_name = tr.xpath(".//td[@data-header='资质名称']/text()")
            cf_name = cf_name[0].strip() if cf_name else ""
            cf_date = tr.xpath(".//td[@data-header='发证日期']/text()")
            cf_date = cf_date[0].strip() if cf_date else ""
            cf_time = tr.xpath(".//td[@data-header='证书有效期']/text()")
            cf_time = cf_time[0].strip() if cf_time else ""
            cf_org = tr.xpath(".//td[@data-header='发证机关']/text()")
            cf_org = cf_org[0].strip() if cf_org else ""
            cf_one.append(cf_type)
            cf_one.append(cf_id)
            cf_one.append(cf_name)
            cf_one.append(cf_date)
            cf_one.append(cf_time)
            cf_one.append(cf_org)
            cf_item["资质信息"].append(cf_one)
        item["data"].append(cf_item)

        # 调用request写的涉诉模块模块
        ss = ZhixingSpider(item["company"])
        ss_list = ss.run()
        ss_item = {}
        ss_item["涉诉信息"] = ss_list
        item["data"].append(ss_item)
        # 调用request写的涉诉模块模块
        shixin = ShixinSpider(item["company"])
        shixin_list = shixin.run()
        shixin_item = {}
        shixin_item["失信情况"] = shixin_list
        item["data"].append(shixin_item)
        # 调用selenium写的文书爬虫
        cp = Cp_spider(item["company"])
        cp_list = cp.run()
        cp_item = {}
        cp_item["文书信息"] = cp_list
        item["data"].append(cp_item)
        return item

    def save_mongodb(self, item):
        self.conn.insert_one(dict(item))
        print("保存成功！")

    def run(self):
        page = 1
        while page<self.company_total:
            response, item = self.start_requests(page)
            self.get_list(response, item)
            page += 1


if __name__ == '__main__':

    z = Qg_jz()
    t0 = time.time()
    z.run()
    t1 = time.time()
    print(t1-t0)






