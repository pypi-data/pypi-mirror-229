# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
本文件实现了常用的工具函数

Authors: xiangyiqing(xiangyiqing@baidu.com)
Date:    2023/07/24
"""
import re

class Dict(dict):
    """dict class"""
    def __getattr__(self, key):
        value = self.get(key, None)
        return Dict(value) if isinstance(value, dict) else value
    
    def __setattr__(self, key, value):
        self[key] = value


def convert_to_dict_object(resp):
    """
    Params
        :resp: dict, response from AIStudio
    Rerurns
        AIStudio object
    """
    if isinstance(resp, dict):
        return Dict(resp)
    
    return resp

def err_resp(sdk_code, msg, biz_code=None):
    """
    Params
        :error_code: sdk错误码
        :msg: 错误信息
        :biz_code: 上游接口错误码透传
    Rerurns
        formatted error msg
    """
    return {
        "error_code": sdk_code,
        "error_msg": msg,
        "biz_code": biz_code
    }


def is_valid_host(host):
    """检测host合法性"""
    # 去除可能的协议前缀 如http://、https://
    host = re.sub(r'^https?://', '', host, flags=re.IGNORECASE)
    return is_valid_domain(host)


def is_valid_domain(domain):
    """检测域名合法性"""
    pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$"
    return re.match(pattern, domain) is not None
