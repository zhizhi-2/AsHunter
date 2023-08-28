#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： zhizhi
# datetime： 2023-08-15 9:33 
# ide： PyCharm
from aiqicha import Aiqicha
from tianyancha import Tianyancha
import setting
import pandas as pd


def get_info(modu):
    """
    使用查询类查询企业信息，并存入表格
    :param modu: 查询类
    :return:
    """
    modu.int_driver()  # 初始化浏览器设置
    modu.get_company_id()  # 获取待搜索企业id
    modu.get_basic_info()  # 获取企业基本信息
    modu.get_websites()  # 获取备案网站
    modu.get_app()  # 获取APP
    modu.get_wechat()  # 获取微信公众号
    modu.get_invest()  # 获取对外投资信息
    modu.quit_driver()  # 关闭浏览器
    log_path = setting.certRecord_path.joinpath('results')
    save_path = log_path.joinpath(f'{modu.source}_{modu.company}.xlsx')
    print(save_path)
    # 将收集到的信息存入文件中
    # with pd.ExcelWriter(save_path) as writer:
    #     website = pd.DataFrame(modu.website)
    #     website.to_excel(writer, sheet_name='备案网站')
    #     app = pd.DataFrame(modu.app)
    #     app.to_excel(writer, sheet_name='APP')
    #     wechat = pd.DataFrame(modu.wechat)
    #     wechat.to_excel(writer, sheet_name='微信公众号')
    #     wechat = pd.DataFrame(modu.invest)
    #     wechat.to_excel(writer, sheet_name='对外投资')


if __name__ == '__main__':
    company = input("请输入查询的企业：")
    aqc = Aiqicha(company)   # 创建爱企查查询类
    get_info(aqc)   # 启动信息收集
    tyc = Tianyancha(company)  # 创建天眼查查询类
    get_info(tyc)   # 启动信息收集

