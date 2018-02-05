# coding=utf-8
import requests
from lxml import etree
from dama import indetify
import time
import random
import datetime
import json
from retrying import retry
import threading
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

# http://shixin.court.gov.cn/findDisNew


class ShixinSpider:

    def __init__(self, company):
        u = Rand_ua()
        ua = u.rand_chose()
        self.session = requests.Session()
        self.headers = {'User-Agent': '{}'.format(ua)}
        self.captcha_url = 'http://shixin.court.gov.cn/captchaNew.do?captchaId=4cda8e1fd7484ec882907acbd70dd519&random={}'
        self.company = company

    @retry(stop_max_attempt_number=5)
    def _search_company(self, name, captcha_url):

        captcha_response = self.session.get(captcha_url, headers=self.headers)
        captcha = indetify(captcha_response.content)
        post_data = {
            "pName": name,
            "pCardNum":"",
            "pProvince":"0",
            "pCode": captcha,
            "captchaId": "4cda8e1fd7484ec882907acbd70dd519"
        }
        resp = self.session.post('http://shixin.court.gov.cn/findDisNew', data=post_data, headers=self.headers)
        print("查询++++++++++", resp.status_code)
        content = resp.content.decode()
        html = etree.HTML(content)
        text = html.xpath("//body//span/text()")[0]
        print("text++++++", text)
        # 处理验证码，超过5次忽略，计入日志
        assert (text != '验证码错误或验证码已过期，请重新输入！' and resp.status_code == 200)
        # with open("html/cw.html","w") as f:
        #     f.write(content)

        # 请求详情页
        ss_list = self.get_detail(html, captcha)
        return ss_list


    def search_company(self, name, captcha_url):
        try:
            ss_list = self._search_company(name, captcha_url)
            # self._search_company(name, captcha_url)

        except:
            with open("log/ss_log.log", 'a') as f:
                now = str(datetime.datetime.now())
                f.write(now + name+ "链接失败或者验证码错误" + '\n')
                ss_list = []

        return ss_list


    def get_detail(self, html, captcha):
        # 判断是否有查询结果,并获取案号id
        ss_list = []
        tr_list = html.xpath("//tbody//tr")
        if len(tr_list)>1:
            for tr in tr_list:
                id = tr.xpath(".//td[@align='center']/a/@id")
                if len(id)>0:
                    ss_one = []
                    id = id[0]
                    # 拼接详情页的链接
                    # http://zhixing.court.gov.cn/search/newdetail?id=16900266&j_captcha=pzt8&captchaId=fda97538121240b38b0c73eeac144dbe&_=1515212716230
                    time_id = int(time.time())*1000
                    # http://shixin.court.gov.cn/disDetailNew?id=700824711&pCode=dfdc&captchaId=4cda8e1fd7484ec882907acbd70dd519
                    # http://shixin.court.gov.cn/disDetailNew?id=702341015&pCode=khce&captchaId=f48ed407d12f4ed5834b5b2ff81eab4f
                    #                                                                           f48ed407d12f4ed5834b5b2ff81eab4f
                    detail_url = "http://shixin.court.gov.cn/disDetailNew?id={}&pCode={}&captchaId=4cda8e1fd7484ec882907acbd70dd519".format(id, captcha)
                    # 发送请求
                    ret = self.session.get(detail_url)
                    print("查看++++++++++",ret.status_code)
                    ret_json = ret.content.decode()
                    '''
                    {"id":701739031,
                    "iname":"广西五鸿建设集团有限公司",
                    "caseCode":"（2017）桂1322执487号",
                    "age":0,
                    "cardNum":"619848910",
                    "businessEntity":"蔡立宗",
                    "courtName":"象州县人民法院",
                    "areaName":"广西",
                    "partyTypeName":"581",
                    "gistId":"（2017）桂1322民初151号",
                    "regDate":"2017年08月11日",
                    "gistUnit":"象州县人民法院",
                    "duty":"被告广西五鸿建设集团有限公司应于本判决生效五日内给付原告甘乃时劳务费人民币48440元。\r\n如果未按本判决指定的期间履行给付金钱义务，应当依照《中华人民共和国民事诉讼法》第二百五十三条之规定，加倍支付迟延履行期间的债务利息。\r\n案件受理费1011元，减半收取505.5元由被告广西五鸿建设集团有限公司负担。","performance":"全部未履行",
                    "performedPart":"暂无",
                    "unperformPart":"暂无",
                    "disruptTypeName":"违反财产报告制度",
                    "publishDate":"2017年11月26日"}
                    '''
                    # 将json 格式转换成python类型
                    ret_dic = json.loads(ret_json)
                    # 获取所需的字段 如果字典没有这个建会报异常
                    try:
                        iname = ret_dic["iname"]
                    except:
                        iname = "未获取到"
                    try:
                        cardNum = ret_dic["cardNum"]# 身份证号码
                    except:
                        cardNum = "未获取到"
                    try:
                        businessEntity = ret_dic["businessEntity"]# 法人
                    except:
                        businessEntity = "未获取到"
                    try:
                        courtName = ret_dic["courtName"]# 执行法院
                    except:
                        courtName = "未获取到"
                    try:
                        areaName = ret_dic["areaName"]# 省份
                    except:
                        areaName = "未获取到"
                    try:
                        gistId = ret_dic["gistId"]# 执行文号
                    except:
                        gistId = "未获取到"
                    try:
                        regDate = ret_dic["regDate"]# 立案时间
                    except:
                        regDate = "未获取到"
                    try:
                        caseCode = ret_dic["caseCode"]# 案号
                    except:
                        caseCode = "未获取到"
                    try:
                        gistUnit = ret_dic["gistUnit"]# 作出执行依据单位
                    except:
                        gistUnit = "未获取到"
                    try:
                        duty = ret_dic["duty"]# 生效法律文书义务
                    except:
                        duty = "未获取到"
                    try:
                        performance = ret_dic["performance"]# 被执行人的履行情况
                    except:
                        performance = "未获取到"
                    try:
                        disruptTypeName = ret_dic["disruptTypeName"]# 失信具体情形
                    except:
                        disruptTypeName = "未获取到"
                    try:
                        publishDate = ret_dic["publishDate"]# 发布时间
                    except:
                        publishDate = "未获取到"

                    ss_one.append(iname)
                    ss_one.append(cardNum)
                    ss_one.append(businessEntity)
                    ss_one.append(courtName)
                    ss_one.append(areaName)
                    ss_one.append(gistId)
                    ss_one.append(regDate)
                    ss_one.append(caseCode)
                    ss_one.append(gistUnit)
                    ss_one.append(duty)
                    ss_one.append(performance)
                    ss_one.append(disruptTypeName)
                    ss_one.append(publishDate)
                    ss_list.append(ss_one)
        print(ss_list)

        return ss_list

    def run(self):
        # 给验证码的url拼接16位随机数
        t0 = time.time()
        captcha_url = self.captcha_url.format(random.randint(999999999999999,9999999999999999)/10000000000000000)
        ss_list = self.search_company(self.company, captcha_url)
        t1 = time.time()
        t_use = t1-t0
        # print(ss_list, t_use)
        # 将详细信息保存到本地
        return ss_list




if __name__ == '__main__':
    company1 = "广西五鸿建设集团有限公司"
    company2 = "上海光华岩土工程勘测设计有限公司"
    c1 = ShixinSpider(company1)
    c2 = ShixinSpider(company2)
    t1 = threading.Thread(target=c2.run)
    t1.start()
    t1.join()
    c1.run()
