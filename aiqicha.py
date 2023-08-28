#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： zhizhi
# datetime： 2023-07-25 10:37 
# ide： PyCharm
"""
爱企查查询类
利用爱企查网站收集资产信息
https://aiqicha.baidu.com
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import numpy as np
from setting import settings
from log import logger


class Aiqicha:
    """
    爱企查企业查询类
    """
    def __init__(self, company):
        self.company = company  # 待查询的企业名字
        self.id = None   # 待搜索企业的id
        self.url = "https://aiqicha.baidu.com"
        self.options = webdriver.EdgeOptions()
        self.source = 'aiqicha'
        self.driver = None
        self.website = []     # 备案网站
        self.domain = []      # 主域名信息
        self.app = []      # APP
        self.wechat = []    # 微信公众号
        self.invest = []    # 对外投资

    def int_driver(self):
        """
        初始化浏览器设置，添加请求头，并隐藏指纹信息
        :return: 设置好的浏览器页面
        """
        logger.log('INFOR', '正在使用爱企查网站获取企业资产信息')
        self.options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36')  # 添加请求头
        self.options.add_argument('headless')  # 设置后台运行，但是会出现安全验证
        self.options.add_argument('window-size=1920x1080')  # 设置浏览器显示大小
        self.options.add_argument('start-maximized')  # 最大显示
        self.options.add_argument('--disable-blink-features=AutomationControlled')  # 避免被检测
        self.driver = webdriver.Edge(options=self.options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                               {"source": 'Object.defineProperty(navigator,"webdriver",{get:()=>undefind})'})

        # 隐藏指纹特征
        min_path = settings.certRecord_path.joinpath('stealth.min.js')
        with open(min_path) as f:
            js = f.read()
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })

    def close_ads(self):
        """
        关闭广告
        :return:
        """
        try:
            self.driver.find_element(By.CLASS_NAME, "icon-close-btn").click()
        except:
            pass

    def quit_driver(self):
        """
        关闭浏览器
        :return:
        """
        self.driver.quit()

    def add_cookies(self):
        """
        添加cookies, self.driver.add_cookie(cookies)添加cookies时要求其必须有name和value字段
        具体可参考https://blog.csdn.net/qew110123/article/details/115335490
        :return:
        """
        try:
            logger.log('INFOR', '尝试加载cookie登录')
            cookies_list = settings.aqc_cookies.split()   # 按空格分割
            for i in cookies_list:
                name, value = i.strip().split("=", 1)
                cookies = {'name': name, 'value': value[:-1] if value.endswith(";") else value}
                self.driver.add_cookie(cookies)
            self.driver.refresh()                # 自动刷新页面，请检查是否已经自动登录账号
            logger.log('INFOR', '加载cookie成功！')
        except:
            logger.log('ALERT', '加载cookie失败')
            self.quit_driver()

    def get_company_id(self):
        """
        获取企业的主页面
        """
        self.driver.get(self.url)
        time.sleep(1)
        self.driver.delete_all_cookies()
        self.add_cookies()   # 加载cookies
        self.driver.maximize_window()  # 最大化浏览器窗口
        try:
            logger.log('INFOR', '尝试搜索该企业')
            self.driver.get(self.url + f'/s?q={self.company}')  # 搜索特定企业
            time.sleep(1)
        except:
            logger.log('ALERT', '尝试搜索失败')
            self.quit_driver()
        self.close_ads()  # 关闭广告
        try:
            time.sleep(2)
            res = self.driver.find_element(By.CLASS_NAME, "company-list")  # 找到第一匹配的企业
            name = res.find_element(By.PARTIAL_LINK_TEXT, self.company)  # 获取匹配企业的名字
            logger.log('INFOR', f'搜索到匹配企业:{name.text.split(" ")[0]}')
            self.id = name.get_attribute("href").split("_")[-1]
            # print(self.id)
        except:
            logger.log('ALERT', '尝试搜索失败')
            self.quit_driver()

    def get_basic_info(self):
        """
        获取企业信息主页面
        :return:
        """
        try:
            logger.log('INFOR', '获取企业主页信息')
            url = self.url + "/company_detail_" + self.id
            self.driver.get(url)
            self.close_ads()  # 关闭广告
        except:
            logger.log('ALERT', '获取失败')
            self.quit_driver()

    def get_websites(self):
        """
        获取备案网站信息
        """
        self.website.append(["序号", "首页地址", "网站名称", "域名", "备案号"])
        time.sleep(2)
        property_rights = self.driver.find_element(By.PARTIAL_LINK_TEXT, "知识产权")  # 获取知识产权按钮
        property_rights.click()
        time.sleep(2)
        try:
            logger.log('INFOR', '正在获取备案网站信息')
            website = self.driver.find_element(By.PARTIAL_LINK_TEXT, "网站备案")   # 获取网站备案按钮
            logger.log('INFOR', f'该企业有{website.text}')
            website.click()
        except:
            logger.log('INFOR', "没有收集到相关备案网站的信息")
            return
        time.sleep(1)
        # 获取网站备案表格信息，并进行内容提取
        table = self.driver.find_element(By.CLASS_NAME, 'aqc-detail-table.certRecord-webRecord-table')
        # 循环获取表格信息
        while True:
            table_body = table.find_element(By.CLASS_NAME, 'table-body')
            table_tr_list = table_body.find_elements(By.TAG_NAME, "tr")
            n = len(table_tr_list)
            for i in range(n):
                table_td_list = table_tr_list[i].find_elements(By.TAG_NAME, "td")
                arr1 = []
                for td in table_td_list:
                    try:
                        # 如果有更多元素按钮则点击查看
                        td.find_element(By.CLASS_NAME, 'more').click()
                        time.sleep(1)
                        text = td.text[:-4]  # 获取除去倒数4个字符的内容
                        arr1.append(text)
                    except:
                        arr1.append(td.text)
                self.website.append(arr1)  # 将表格数据组成二维的列表
            try:
                # 点击下一页
                self.driver.find_element(By.CSS_SELECTOR, '#certRecord-webRecord>div>div>ul>li.ivu-page-next>a').click()
            except:
                break
            time.sleep(1)
        logger.log('INFOR', f'已成功获取到{len(self.website) - 1}条备案网站信息')

    def get_domain(self):
        """
        从备案网站信息中提取主域名信息
        :return:
        """
        domain = np.array(self.website)[1:, 3]
        for item in domain:
            if '\n' in item:
                self.domain.extend(item.split('\n')[:-1])
            else:
                self.domain.append(item)

        logger.log('INFOR', f'已成功获取到{len(self.domain)}条主域名信息')

    def get_app(self):
        """
        获取APP信息
        """
        # 点击经营状况按钮
        self.driver.find_element(By.PARTIAL_LINK_TEXT, "经营状况").click()
        time.sleep(2)
        try:
            logger.log('INFOR', '正在获取APP信息')
            appinfo = self.driver.find_element(By.CLASS_NAME, "item.subtab-appinfo")    # 获取APP信息按钮
            logger.log('INFOR', f'该企业有{appinfo.text}')
            appinfo.click()
        except:
            logger.log('INFOR', "没有收集到相关APP的信息")
            return
        time.sleep(1)
        # 获取APP信息表格，并提取其中的内容
        table = self.driver.find_element(By.CLASS_NAME, 'aqc-detail-table.operatingCondition-appinfo-table')
        table_header = table.find_element(By.CLASS_NAME, 'aqc-detail-thead')
        table_tr_list = table_header.find_elements(By.TAG_NAME, "tr")
        # 获取表头
        for td in table_tr_list:
            arr1 = (td.text).split(" ")
            # print(arr1)
            self.app.append(arr1)

        while True:
            table_body = table.find_element(By.CLASS_NAME, 'table-body')
            table_tr_list = table_body.find_elements(By.TAG_NAME, "tr")
            n = len(table_tr_list)
            # 按行查询表格的数据，取出的数据是一整行，按空格分隔每一列的数据
            for i in range(n):
                table_td_list = table_tr_list[i].find_elements(By.TAG_NAME, "td")
                arr1 = []
                for td in table_td_list:
                    try:
                        see_more = td.find_element(By.CLASS_NAME, 'fold-btn.fold')  # 包含查看更多元素
                        see_more.click()
                        time.sleep(1)
                        text = td.text[:-2]
                        arr1.append(text)
                    except:
                        arr1.append(td.text)
                # print(arr1)
                self.app.append(arr1)  # 将表格数据组成二维的列表
            try:
                # 点击下一页，不存在下一页则结束内容提取
                self.driver.find_element(By.CSS_SELECTOR, '#operatingCondition-appinfo>div.aqc-table-list-pager>div>ul>li.ivu-page-next>a').click()
            except:
                break
            time.sleep(1)
        logger.log('INFOR', f'已成功获取到{len(self.app) - 1}条app信息')

    def get_wechat(self):
        """
        获取微信公众号信息
        :param driver:
        :return:
        """
        # 点击经营状况按钮
        self.driver.find_element(By.PARTIAL_LINK_TEXT, "经营状况").click()
        time.sleep(2)
        try:
            logger.log('INFOR', '正在获取微信公众号信息')
            wechatoa = self.driver.find_element(By.CLASS_NAME, "item.subtab-wechatoa")  #
            logger.log('INFOR', f'该企业有{wechatoa.text}')
            wechatoa.click()
        except:
            logger.log('INFOR', "没有收集到相关微信公众号的信息")
            return
        time.sleep(1)
        # 获取微信公众号信息表格，
        table = self.driver.find_element(By.CLASS_NAME, 'aqc-detail-table.operatingCondition-wechatoa-table')
        table_header = table.find_element(By.CLASS_NAME, 'aqc-detail-thead')
        table_tr_list = table_header.find_elements(By.TAG_NAME, "tr")
        # 获取表头
        for td in table_tr_list:
            arr1 = (td.text).split(" ")
            # print(arr1)
            self.wechat.append(arr1)

        while True:
            table_body = table.find_element(By.CLASS_NAME, 'table-body')
            table_tr_list = table_body.find_elements(By.TAG_NAME, "tr")
            n = len(table_tr_list)
            # 按行查询表格的数据，取出的数据是一整行，按空格分隔每一列的数据
            for i in range(n):
                table_td_list = table_tr_list[i].find_elements(By.TAG_NAME, "td")
                arr1 = []
                for td in table_td_list:
                    try:
                        see_more = td.find_element(By.CLASS_NAME, 'fold-btn.fold')  # 包含查看更多元素
                        see_more.click()
                        time.sleep(1)
                        text = td.text[:-2]
                        arr1.append(text)
                    except:
                        arr1.append(td.text)
                # print(arr1)
                self.wechat.append(arr1)  # 将表格数据组成二维的列表
            try:
                self.driver.find_element(By.CSS_SELECTOR,
                                        '#operatingCondition-wechatoa>div.aqc-table-list-pager>div>ul>li.ivu-page-next>a').click()  # 点击下一页
            except:
                break
            time.sleep(1)
        logger.log('INFOR', f'已成功获取到{len(self.wechat) - 1}条微信公众号信息')

    def get_invest(self):
        """
        获取投资子公司信息
        :return:
        """
        time.sleep(1)
        self.driver.save_screenshot("1.png")
        self.driver.find_element(By.PARTIAL_LINK_TEXT, "基本信息").click()   # 点击基本信息按钮
        time.sleep(2)
        try:
            logger.log('INFOR', '正在获取对外投资信息')
            invest = self.driver.find_element(By.CLASS_NAME, "item.subtab-invest")  # 点击对外投资按钮
            logger.log('INFOR', f'该企业有{invest.text}')
            invest.click()
        except:
            logger.log('INFOR', "没有收集到对外投资的信息")
            return
        time.sleep(1)
        # 获取对外投资信息表格，
        table = self.driver.find_element(By.CLASS_NAME, 'aqc-detail-table.basic-invest-table')
        table_header = table.find_element(By.CLASS_NAME, 'aqc-detail-thead')
        table_tr_list = table_header.find_elements(By.TAG_NAME, "tr")
        # 获取表头
        for td in table_tr_list:
            arr1 = td.text.split(" ")
            arr1.insert(1, 'company_link')
            # print(arr1)
            self.invest.append(arr1)

        while True:
            table_body = table.find_element(By.CLASS_NAME, 'table-body')
            table_tr_list = table_body.find_elements(By.TAG_NAME, "tr")[:-1]  # 去除最后一个条目，因为最后一个条目即表示本公司
            n = len(table_tr_list)
            # 按行查询表格的数据，取出的数据是一整行，按空格分隔每一列的数据
            for i in range(n):
                table_td_list = table_tr_list[i].find_elements(By.TAG_NAME, "td")
                arr1 = []
                for td in table_td_list:
                    arr1.append(td.text)
                href = table_td_list[1].find_element(By.TAG_NAME, 'a')  # 包含查看更多元素
                id = href.get_attribute("href")
                arr1.insert(1, id)
                # print(arr1)
                self.invest.append(arr1)  # 将表格数据组成二维的列表
            try:
                # 有下一页则点击下一页, 否则结束提取
                self.driver.find_element(By.CSS_SELECTOR,
                                         '#basic-invest>div.aqc-table-list-pager>div>ul>li.ivu-page-next>a').click()
            except:
                break
            time.sleep(1)
        logger.log('INFOR', f'已成功获取到{len(self.invest) - 1}条对外投资信息')


if __name__ == '__main__':
    company = input("请输入查询的企业：")
    aqc = Aiqicha(company)  # 创建爱企查查询类
    aqc.int_driver()   # 初始化浏览器设置
    aqc.get_company_id()   # 获取待搜索企业id
    aqc.get_basic_info()  # 获取企业基本信息
    aqc.get_websites()   # 获取备案网站
    aqc.get_domain()    # 主域名信息
    aqc.get_app()      # 获取APP
    aqc.get_wechat()   # 获取微信公众号
    aqc.get_invest()     # 获取对外投资信息
    aqc.quit_driver()   # 关闭
    log_path = settings.certRecord_path.joinpath('results')
    save_path = log_path.joinpath(f'{aqc.source}_{company}.xlsx')  # 保存信息的路径
    print(save_path)
    print(aqc.website)
    print(aqc.domain)
    print(aqc.wechat)
    print(aqc.app)
    print(aqc.invest)
    # 将信息存入表格
    with pd.ExcelWriter(save_path) as writer:
        website = pd.DataFrame(aqc.website)
        website.to_excel(writer, sheet_name='备案网站')
        app = pd.DataFrame(aqc.app)
        app.to_excel(writer, sheet_name='APP')
        wechat = pd.DataFrame(aqc.wechat)
        wechat.to_excel(writer, sheet_name='微信公众号')
        wechat = pd.DataFrame(aqc.invest)
        wechat.to_excel(writer, sheet_name='对外投资')
