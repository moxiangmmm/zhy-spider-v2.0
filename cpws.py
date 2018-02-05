# coding=utf-8

from selenium import webdriver
import time
from handel_html import Handel_html
from rand_ua import Rand_ua

# 遍历企业名单列表
# 使用随机的ua去访问
# 先打开完站搜索框输入关键字
# 点击搜索
# 等网页加载完后获取网页源码
# 筛选出所需要的字段保存
# 优化方案：
# 使用随机ip
# 补充完整的headers


class Cp_spider():

    def __init__(self, key_word):

        u = Rand_ua()
        ua = u.rand_chose()
        options = webdriver.ChromeOptions()
        options.add_argument('--user-agent={}'.format(ua))
        self.driver = webdriver.Chrome(chrome_options=options)
        self.cp_url = "http://wenshu.court.gov.cn/"
        self.key_word = key_word

    def get_info(self):
        # self.driver.implicitly_wait(15) # 显性等待
        self.driver.get(self.cp_url)
        self.driver.find_element_by_xpath('//input[@id="gover_search_key"]').click()
        self.driver.find_element_by_xpath('//input[@id="gover_search_key"]').send_keys(self.key_word)
        self.driver.find_element_by_xpath("//button[@class='head_search_btn']").click()

        time.sleep(10)
        html_list = []
        page = 1
        while 1:
            # [['（2016）京01民终7217号', '2016-12-19', '北京市第一中级人民法院', '魏巍等劳动争议二审民事判决书', ['民事', '二审'], 'http://wenshu.court.gov.cn/content/content?DocID=d4117425-9198-40a2-8a98-3711404e253b&KeyWord=深圳市中合银融资担保有限公司'], ['（2017）粤03民终2926号', '2017-05-12', '广东省深圳市中级人民法院', '江西中联建设集团有限公司与', ['民事', '二审'], 'http://wenshu.court.gov.cn/content/content?DocID=5d5cf5a2-2531-416b-9516-a85101011a03&KeyWord=深圳市中合银融资担保有限公司'], ['（2016）粤03民辖终3827、3828号', '2016-11-17', '广东省深圳市中级人民法院', '旭东电力集团有限公司与', ['民事', '二审'], 'http://wenshu.court.gov.cn/content/content?DocID=fe883891-d1a8-44a3-a23c-1f67a0349cb7&KeyWord=深圳市中合银融资担保有限公司'], ['（2016）粤0304民初18775-18776号', '2016-09-21', '深圳市福田区人民法院', '与旭东电力集团有限公司罗云富保证合同纠纷一审民事裁定书', ['民事', '一审'], 'http://wenshu.court.gov.cn/content/content?DocID=1c55cb08-667d-48eb-9dae-a7f4010e73cc&KeyWord=深圳市中合银融资担保有限公司'], ['（2016）粤0304民初18775-18776号之一', '2017-07-10', '深圳市福田区人民法院', '与旭东电力集团有限公司、罗云富保证合同纠纷一审民事裁定书', ['民事', '一审'], 'http://wenshu.court.gov.cn/content/content?DocID=197c2dfb-7520-4b7d-9598-a7f4010e73f2&KeyWord=深圳市中合银融资担保有限公司']]
            html = self.driver.page_source

            html_list.append(html)
            try:
                self.driver.implicitly_wait(15)
                self.driver.find_element_by_xpath('//a[@class="next"]').click()
            except:
                # 将错误写入日志
                # print('发生异常')
                self.driver.quit()
                break
            time.sleep(10)
            page += 1
        return html_list

    def run(self):
        html_list = self.get_info()
        h = Handel_html(html_list)
        cp_list = h.run()
        cp_list.append(len(cp_list))
        return cp_list

if __name__ == '__main__':
    key_word = '深圳市中合银融资担保有限公司'
    c = Cp_spider(key_word)
    cp_list = c.run()
    print(cp_list)




