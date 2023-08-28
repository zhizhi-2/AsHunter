#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： zhizhi
# datetime： 2023-08-14 10:37
# ide： PyCharm
"""
天眼查查询类
利用天眼查网站收集资产信息
https://www.tianyancha.com
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import numpy as np
from setting import settings
from log import logger


class Tianyancha:
    """
    天眼查企业查询类
    """
    def __init__(self, company):
        self.company = company
        self.id = None   # 带搜索企业的id
        self.url = "https://www.tianyancha.com"
        self.options = webdriver.EdgeOptions()
        self.source = 'tianyancha'
        self.driver = None
        self.website = []     # 备案网站
        self.domain = []  # 主域名信息
        self.app = []      # APP
        self.wechat = []    # 微信公众号
        self.invest = []    # 对外投资


    def int_driver(self):
        """
        初始化浏览器设置
        :return:
        """
        logger.log('INFOR', '正在使用天眼查网站获取企业资产信息')
        self.options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36')  # 添加请求头
        self.options.add_argument('headless')  # 设置后台运行
        self.options.add_argument('window-size=1920x1080')  # 设置浏览器显示大小
        self.options.add_argument('start-maximized')  # 最大显示
        self.options.add_argument('--disable-blink-features=AutomationControlled')  # 避免被检测
        self.driver = webdriver.Edge(options=self.options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                               {"source": 'Object.defineProperty(navigator,"webdriver",{get:()=>undefind})'})

        # 隐藏指纹特征
        min_path = settings.data_storage_dir.joinpath('stealth.min.js')
        with open(min_path) as f:
            js = f.read()
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })

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
            cookies_list = settings.tyc_cookies.split()   # 按空格分割
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
            self.driver.get(self.url + f'/search?key={self.company}')  # 搜索特定企业
            time.sleep(1)
        except:
            logger.log('ALERT', '尝试搜索失败')
            self.quit_driver()
        try:
            time.sleep(2)
            res = self.driver.find_element(By.CLASS_NAME, "index_alink__zcia5.link-click")  # 找到第一匹配的企业
            logger.log('INFOR', f'搜索到匹配企业:{res.text.split(" ")[0]}')
            self.id = res.get_attribute("href").split("/")[-1]
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
            url = self.url + "/company/" + self.id
            self.driver.get(url)
        except:
            logger.log('ALERT', '获取失败')
            self.quit_driver()

    def get_websites(self):
        """
        获取备案网站信息
        """
        time.sleep(2)
        property_rights = self.driver.find_element(By.PARTIAL_LINK_TEXT, "知识产权")  # 获取知识产权按钮
        property_rights.click()
        time.sleep(2)
        try:
            logger.log('INFOR', '正在获取备案网站信息')
            website = self.driver.find_element(By.PARTIAL_LINK_TEXT, "网站备案")       # 获取网站备案按钮
            logger.log('INFOR', f'该企业有{website.text}')
            website.click()
        except:
            logger.log('INFOR', "没有收集到相关备案网站的信息")
            return
        time.sleep(1)
        # 获取网站备案表格信息，并进行内容提取
        element = self.driver.find_element(By.CLASS_NAME, 'dim-group.dim-group.index_company-knowledge-root__574N5')
        element = element.find_elements(By.CLASS_NAME, 'dim-section')[-1]
        table = element.find_element(By.TAG_NAME, 'table')
        table_header = table.find_element(By.CLASS_NAME, 'table-thead')
        tr = table_header.find_element(By.TAG_NAME, "tr")
        td_list = tr.find_elements(By.TAG_NAME, "td")
        # 获取表头
        arr1 = []
        for td in td_list:
            arr1.append(td.text)
        # print(arr1)
        self.website.append(arr1)

        while True:
            table_body = table.find_element(By.TAG_NAME, 'tbody')
            table_tr_list = table_body.find_elements(By.TAG_NAME, "tr")
            n = len(table_tr_list)
            for i in range(n):
                table_td_list = table_tr_list[i].find_elements(By.TAG_NAME, "td")
                arr1 = []
                for td in table_td_list:
                    arr1.append(td.text)
                # print(arr1)
                self.website.append(arr1)  # 将表格数据组成二维的列表
            try:
                # 有下一页则跳转
                element.find_element(By.CLASS_NAME, 'tic.tic-laydate-next-m').click()
            except:
                break
            time.sleep(1)
        logger.log('INFOR', f'已成功获取到{len(self.website) - 1}条备案网站信息')

    def get_domain(self):
        """
        从备案网站信息中提取主域名信息
        :return:
        """
        domain = np.array(self.website)[1:, 4]  # 提取除第一行的第四列信息
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
            appinfo = self.driver.find_element(By.PARTIAL_LINK_TEXT, "产品信息")    # 获取APP信息按钮
            logger.log('INFOR', f'该企业有{appinfo.text}')
            appinfo.click()
        except:
            logger.log('INFOR', "没有收集到相关APP的信息")
            return
        time.sleep(1)
        # 获取APP信息表格，并提取其中的内容
        element = self.driver.find_element(By.CLASS_NAME, 'dim-group.dim-group')
        element = element.find_elements(By.CLASS_NAME, 'dim-section')[10]
        table = element.find_element(By.TAG_NAME, 'table')     # 定位到对应表格
        table_header = table.find_element(By.CLASS_NAME, 'table-thead')  # 表头
        tr = table_header.find_element(By.TAG_NAME, "tr")
        td_list = tr.find_elements(By.TAG_NAME, "td")
        # 获取表头
        arr1 = []
        for td in td_list:
            arr1.append(td.text)
        print(arr1)
        self.app.append(arr1)
        # 循环提取表格中的内容
        while True:
            table_body = table.find_element(By.TAG_NAME, 'tbody')
            table_tr_list = table_body.find_elements(By.TAG_NAME, "tr")
            n = len(table_tr_list)
            # 按行查询表格的数据，取出的数据是一整行，按空格分隔每一列的数据
            for i in range(n):
                table_td_list = table_tr_list[i].find_elements(By.TAG_NAME, "td")
                arr1 = []
                for td in table_td_list:
                    arr1.append(td.text)
                print(arr1)
                self.app.append(arr1)  # 将表格数据组成二维的列表
            try:
                # 点击下一页，不存在下一页则结束内容提取
                element.find_element(By.CLASS_NAME, 'tic.tic-laydate-next-m').click()
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
            wechatoa = self.driver.find_element(By.PARTIAL_LINK_TEXT, "微信公众号")  #
            logger.log('INFOR', f'该企业有{wechatoa.text}')
            wechatoa.click()
        except:
            logger.log('INFOR', "没有收集到相关微信公众号的信息")
            return
        time.sleep(1)
        # 获取微信公众号信息表格，
        element = self.driver.find_element(By.CLASS_NAME, 'dim-group.dim-group')
        element = element.find_elements(By.CLASS_NAME, 'dim-section')[11]
        table = element.find_element(By.TAG_NAME, 'table')
        table_header = table.find_element(By.CLASS_NAME, 'table-thead')  # 表头
        tr = table_header.find_element(By.TAG_NAME, "tr")
        td_list = tr.find_elements(By.TAG_NAME, "td")
        # 获取表头
        arr1 = []
        for td in td_list:
            arr1.append(td.text)
        # print(arr1)
        self.wechat.append(arr1)

        while True:
            table_body = table.find_element(By.TAG_NAME, 'tbody')
            table_tr_list = table_body.find_elements(By.TAG_NAME, "tr")
            n = len(table_tr_list)
            # 按行查询表格的数据，取出的数据是一整行，按空格分隔每一列的数据
            for i in range(n):
                table_td_list = table_tr_list[i].find_elements(By.TAG_NAME, "td")
                arr1 = []
                for td in table_td_list:
                    arr1.append(td.text)
                # print(arr1)
                self.wechat.append(arr1)  # 将表格数据组成二维的列表
            try:
                # 点击下一页，不存在下一页则结束内容提取
                element.find_element(By.CLASS_NAME, 'tic.tic-laydate-next-m').click()
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
        self.driver.find_element(By.PARTIAL_LINK_TEXT, "企业背景").click()   # 点击企业背景按钮
        time.sleep(2)
        try:
            logger.log('INFOR', '正在获取对外投资信息')
            invest = self.driver.find_element(By.PARTIAL_LINK_TEXT, "对外投资")  # 点击对外投资按钮
            logger.log('INFOR', f'该企业有{invest.text}')
            invest.click()
        except:
            logger.log('INFOR', "没有收集到对外投资的信息")
            return
        time.sleep(1)
        # 获取对外投资信息表格，
        element = self.driver.find_element(By.ID, 'inverst-table')
        table = element.find_element(By.TAG_NAME, 'table')
        table_header = table.find_element(By.CLASS_NAME, 'table-thead')  # 表头
        tr = table_header.find_element(By.TAG_NAME, "tr")
        td_list = tr.find_elements(By.TAG_NAME, "td")
        # 获取表头
        arr1 = []
        for td in td_list:
            arr1.append(td.text)
        arr1.insert(1, 'company_link')
        # print(arr1)
        self.invest.append(arr1)

        while True:
            table_body = table.find_element(By.TAG_NAME, 'tbody')
            table_tr_list = table_body.find_elements(By.TAG_NAME, "tr")
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
                # 点击下一页，不存在下一页则结束内容提取
                element.find_element(By.CLASS_NAME, 'tic.tic-laydate-next-m').click()
            except:
                break
            time.sleep(1)
        logger.log('INFOR', f'已成功获取到{len(self.invest) - 1}条对外投资信息')


if __name__ == '__main__':
    company = input("请输入查询的企业：")
    tyc = Tianyancha(company)  # 创建爱企查查询类
    tyc.int_driver()    # 初始化浏览器设置
    tyc.get_company_id()   # 获取待搜索企业id
    tyc.get_basic_info()  # 获取企业基本信息
    tyc.get_websites()   # 获取备案网站
    tyc.get_domain()    # 获取主域名信息
    tyc.get_app()      # 获取APP
    tyc.get_wechat()   # 获取微信公众号
    tyc.get_invest()     # 获取对外投资信息
    tyc.quit_driver()   # 关闭
    log_path = settings.certRecord_path.joinpath('results')
    save_path = log_path.joinpath(f'{tyc.source}_{company}.xlsx')
    print(save_path)
    print(tyc.website)
    print(tyc.domain)
    # 将信息存入表格
    with pd.ExcelWriter(save_path) as writer:
        website = pd.DataFrame(tyc.website)
        website.to_excel(writer, sheet_name='备案网站')
        app = pd.DataFrame(tyc.app)
        app.to_excel(writer, sheet_name='APP')
        wechat = pd.DataFrame(tyc.wechat)
        wechat.to_excel(writer, sheet_name='微信公众号')
        invest = pd.DataFrame(tyc.invest)
        invest.to_excel(writer, sheet_name='对外投资')
