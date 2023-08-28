#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： zhizhi
# datetime： 2023-08-17 11:10 
# ide： PyCharm

def merge_website(aqc, tyc, column):
    """
    合并爱企查和天眼查查询的备案网站信息，并去重
    :param aqc: 爱企查的查询结果
    :param tyc: 天眼查的查询结果
    :param column: 去重的根据
    :return:
    """
    result = []
    merged_values = set()

    for item in aqc:
        key = item[column]
        if key not in merged_values:
            result.append(item)
            merged_values.add(key)

    for item in tyc:
        key = item[column]
        if key not in merged_values:
            result.append(item)
            merged_values.add(key)
    return result


def merge_app(aqc, tyc, column):
    """
    合并爱企查和天眼查查询的APP信息，并去重
    :param aqc: 爱企查的查询结果
    :param tyc: 天眼查的查询结果
    :param column: 去重的列数
    :return:
    """
    result = []
    merged_values = set()

    for item in aqc:
        key = item[column]
        if key not in merged_values:
            result.append(item)
            merged_values.add(key)

    for item in tyc:
        key = item[column]
        if key not in merged_values:
            result.append(item)
            merged_values.add(key)
    return result


def merge_wechat(aqc, tyc, column):
    """
    合并爱企查和天眼查查询的微信公众号信息，并去重
    :param aqc: 爱企查的查询结果
    :param tyc: 天眼查的查询结果
    :param column: 去重的列数
    :return:
    """
    result = []
    merged_values = set()

    for item in aqc:
        key = item[column]
        if key not in merged_values:
            result.append(item)
            merged_values.add(key)

    for item in tyc:
        key = item[column]
        if key not in merged_values:
            result.append(item)
            merged_values.add(key)
    return result


if '__name__' == '__main__':
    list1 = [[0, 1, 2], [1, 2, 3], [1, 3, 5]]
    list2 = [[0, 1, 2], [1, 2, 3], [1, 4, 7]]

    res = merge_website(list1, list2, 2)
    print(res)