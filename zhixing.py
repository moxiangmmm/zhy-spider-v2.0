# coding=utf-8
import requests
from lxml import etree
from dama import indetify
import time
import random
import datetime
import json
from retrying import retry
from rand_ua import Rand_ua

# 读取客户名单中的公司名称
# for循环遍历
# 判断验证码是否错误，如错重新请求
# 判断是查询结果是否有内容，如有请求详情页信息
# 获取案号id
# 拼接参数，发送GET请求
# 下载源代码保存到本地
# 用retry装饰函数，如果验证码错误就抛异常，最多尝试5次

# 根据传过来的参数发送请求检索是否有诉信息
# 如果没有则返回一个空列表
# 如果有则遍历每一行信息，并把字段添加到一个列表中
# 再把各个列表添加到一个列表中返回


class ZhixingSpider:

    def __init__(self, company):
        u = Rand_ua()
        ua = u.rand_chose()
        self.session = requests.Session()
        self.headers = {'User-Agent': '{}'.format(ua)}
        self.captcha_url = 'http://zhixing.court.gov.cn/search/captcha.do?captchaId=fda97538121240b38b0c73eeac144dbe&random={}'
        self.company = company

    @retry(stop_max_attempt_number=5)
    def _search_company(self, name, captcha_url):

        captcha_response = self.session.get(captcha_url, headers=self.headers)
        captcha = indetify(captcha_response.content)
        post_data = {
            "searchCourtName": "全国法院（包含地方各级法院）",
            "selectCourtId": 1,
            "selectCourtArrange": 1,
            "pname": name,
            "cardNum": "",
            "j_captcha": captcha,
            "captchaId": "fda97538121240b38b0c73eeac144dbe"
        }
        # print(post_data)
        resp = self.session.post('http://zhixing.court.gov.cn/search/newsearch', data=post_data, headers=self.headers)
        print("查询++++++++++", resp.status_code)
        content = resp.content.decode()
        html = etree.HTML(content)
        # 判断验证码是否错误
        text = html.xpath("//title/text()")[0]
        print("+++++text", text)
        # 处理验证码，超过5次忽略，计入日志
        assert (text != "验证码出现错误，请重新输入！" and resp.status_code == 200)
        # 请求详情页
        ss_list = self.get_detail(html, captcha)

        return ss_list


    def search_company(self, name, captcha_url):
        try:
            ss_list = self._search_company(name, captcha_url)

        except:
            with open("log/shesu_log.log", 'a') as f:
                now = str(datetime.datetime.now())
                f.write(now + name+ "链接失败或者验证码错误" + '\n')
                ss_list = []

        return ss_list



    def get_detail(self, html, captcha):
        # 判断是否有查询结果,并获取案号id
        ss_list = []
        tr_list = html.xpath("//tbody//tr")
        # print(tr_list)
        if len(tr_list)>1:
            print("*" * 20)
            for tr in tr_list:
                id = tr.xpath(".//td[@align='center']/a/@id")
                if len(id)>0:
                    ss_one = []
                    id = id[0]
                    # print(id)
                    # 拼接详情页的链接
                    # http://zhixing.court.gov.cn/search/newdetail?id=16900266&j_captcha=pzt8&captchaId=fda97538121240b38b0c73eeac144dbe&_=1515212716230
                    time_id = int(time.time())*1000
                    detail_url = "http://zhixing.court.gov.cn/search/newdetail?id={}&j_captcha={}&captchaId=fda97538121240b38b0c73eeac144dbe&_={}".format(id, captcha, time_id)
                    # 发送请求
                    ret = self.session.get(detail_url)
                    print("查看++++++++++",ret.status_code)
                    ret_json = ret.content.decode()
                    # 将json 格式转换成python类型
                    ret_dic = json.loads(ret_json)
                    # 获取所需的字段 如果字典没有这个建会报异常
                    try:
                        pname = ret_dic["pname"]
                    except:
                        pname = "未获取到"
                    try:
                        caseCode = ret_dic["caseCode"]# 案号
                    except:
                        caseCode = "未获取到"
                    try:
                        caseCreateTime = ret_dic["caseCreateTime"] # 立案时间
                    except:
                        caseCreateTime = "未获取到"
                    try:
                        partyCardNum = ret_dic["partyCardNum"]# 身份证号码
                    except:
                        partyCardNum = "未获取到"
                    try:
                        execCourtName = ret_dic["execCourtName"]# 执行法院
                    except:
                        execCourtName = "未获取到"
                    try:
                        execMoney = ret_dic["execMoney"]# 执行标的
                    except:
                        execMoney = "未获取到"
                    ss_one.append(pname)
                    ss_one.append(caseCode)
                    ss_one.append(caseCreateTime)
                    ss_one.append(partyCardNum)
                    ss_one.append(execCourtName)
                    ss_one.append(execMoney)
                    ss_list.append(ss_one)

        return ss_list

    def run(self):
        # 给验证码的url拼接16位随机数
        t0 = time.time()
        captcha_url = self.captcha_url.format(random.randint(999999999999999,9999999999999999)/10000000000000000)
        ss_list = self.search_company(self.company, captcha_url)
        t1 = time.time()
        t_use = t1-t0
        print(ss_list, t_use)
        # 将详细信息保存到本地
        return ss_list



if __name__ == '__main__':
    company = "广西五鸿建设集团有限公司"
    company = ZhixingSpider(company)
    company.run()