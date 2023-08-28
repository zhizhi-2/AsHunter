#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： zhizhi
# datetime： 2023-08-14 14:19 
# ide： PyCharm
"""
配置文件
"""
import pathlib


class Setting:
    def __init__(self):
        # 相对路径
        self.certRecord_path = pathlib.Path(__file__).parent
        # 爱企查cookie
        self.aqc_cookies = ''
        self.tyc_cookies = ''
        # 企查查cookie
        # self.qcc_cookies = ''


settings = Setting()