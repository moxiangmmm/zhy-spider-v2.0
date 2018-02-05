# coding=utf-8
from lxml import etree

class Handel_html(object):

    def __init__(self, html_list):
        self.html_list = html_list
        self.cp_list = []

    def handel(self, html):
        xml = etree.HTML(html)
        div_list = xml.xpath("//div[@id='resultList']//div[@class='dataItem']")
        for div in div_list:
            cp_one = []
            jieduan = div.xpath(".//div[@class='label']//text()")
            jd = jieduan[0] + jieduan[1] if len(jieduan)>1 else '未获取到' # 阶段
            href = div.xpath(".//tbody//tr[1]//a/@href")
            doc_href = "http://wenshu.court.gov.cn" + href[1] if len(href)>1 else "未获取到"
            t = div.xpath(".//div[@class='wstitle']//a/text()")
            title = t[0] if len(t)>1 else "未获取到" # 标题
            info = div.xpath(".//tbody//tr[2]//text()") # 信息
            if len(info) > 0:
                info_list = info[0].split("\xa0\xa0\xa0\xa0")
                # ['深圳市福田区人民法院', '（2016）粤0304民初18775-18776号之一', '2017-07-10']
                fa_yuan = info_list[0]
                id = info_list[1]
                date = info_list[2]
            else:
                fa_yuan = '未获取到'
                id = '未获取到'
                date = '未获取到'
            cp_one.append(id)
            cp_one.append(date)
            cp_one.append(fa_yuan)
            cp_one.append(title)
            cp_one.append(jd)
            cp_one.append(doc_href)
            self.cp_list.append(cp_one)


    # 获取结果总数
    def get_total(self, html_list):
        t_list = []
        for html in html_list:
            xml = etree.HTML(html)
            total = xml.xpath("//span[@id='span_datacount']//text()")
            t = total[0] if total else "未获取到总条数"
            t_list.append(t)
        t = t_list[0]
        return t


    def run(self):
        for html in self.html_list:
            self.handel(html)
        t = self.get_total(self.html_list)
        self.cp_list.append(t)
        return self.cp_list


if __name__ == '__main__':
    html_list = []
    with open('html/深圳市中合银融资担保有限公司_1.html','r') as f:
        html1 = f.read()
    with open('html/深圳市中合银融资担保有限公司_2.html','r') as f:
        html2 = f.read()
    html_list.append(html1)
    html_list.append(html2)
    h = Handel_html(html_list)
    cp_list = h.run()
    print(cp_list)



# [['（2016）京01民终7217号', '2016-12-19', '北京市第一中级人民法院', '魏巍等劳动争议二审民事判决书', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=d4117425-9198-40a2-8a98-3711404e253b&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2017）粤03民终2926号', '2017-05-12', '广东省深圳市中级人民法院', '江西中联建设集团有限公司与', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=5d5cf5a2-2531-416b-9516-a85101011a03&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤03民辖终3827、3828号', '2016-11-17', '广东省深圳市中级人民法院', '旭东电力集团有限公司与', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=fe883891-d1a8-44a3-a23c-1f67a0349cb7&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤0304民初18775-18776号', '2016-09-21', '深圳市福田区人民法院', '与旭东电力集团有限公司罗云富保证合同纠纷一审民事裁定书', '民事一审', 'http://wenshu.court.gov.cn/content/content?DocID=1c55cb08-667d-48eb-9dae-a7f4010e73cc&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤0304民初18775-18776号之一', '2017-07-10', '深圳市福田区人民法院', '与旭东电力集团有限公司、罗云富保证合同纠纷一审民事裁定书', '民事一审', 'http://wenshu.court.gov.cn/content/content?DocID=197c2dfb-7520-4b7d-9598-a7f4010e73f2&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）京01民终7217号', '2016-12-19', '北京市第一中级人民法院', '魏巍等劳动争议二审民事判决书', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=d4117425-9198-40a2-8a98-3711404e253b&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2017）粤03民终2926号', '2017-05-12', '广东省深圳市中级人民法院', '江西中联建设集团有限公司与', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=5d5cf5a2-2531-416b-9516-a85101011a03&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤03民辖终3827、3828号', '2016-11-17', '广东省深圳市中级人民法院', '旭东电力集团有限公司与', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=fe883891-d1a8-44a3-a23c-1f67a0349cb7&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤0304民初18775-18776号', '2016-09-21', '深圳市福田区人民法院', '与旭东电力集团有限公司罗云富保证合同纠纷一审民事裁定书', '民事一审', 'http://wenshu.court.gov.cn/content/content?DocID=1c55cb08-667d-48eb-9dae-a7f4010e73cc&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤0304民初18775-18776号之一', '2017-07-10', '深圳市福田区人民法院', '与旭东电力集团有限公司、罗云富保证合同纠纷一审民事裁定书', '民事一审', 'http://wenshu.court.gov.cn/content/content?DocID=197c2dfb-7520-4b7d-9598-a7f4010e73f2&KeyWord=深圳市中合银融资担保有限公司']]
