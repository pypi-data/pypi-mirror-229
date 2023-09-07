# -*- coding: utf-8 -*-
"""
@File    : cert_util_test.py
@Date    : 2022-10-22
@Author  : Peng Shiyu
"""
import re

from domain_admin.utils import whois_util
from domain_admin.utils import text_util
from domain_admin.utils.whois_util.config import ROOT_SERVER
from domain_admin.utils.whois_util.util import get_whois_raw, parse_whois_raw


def test_get_domain_info():
    domain_list = [
        # cn
        # 'www.baidu.cn',

        # com
        # 'www.xiaomi.com',
        # 'dfyun-spare1.showdoc.com.cn:8888',

        # net
        # 'csdn.net',
        # 'jb51.net',
        # '126.net'

        # biz
        # 'all.biz'

        # 'dot.tk'
        # 'bilibili.tv'
        # 'wowma.jp'
        # 'www.otto.de',
        # 'www.米梵家居.com'
        '中万.中国',
        '中万.公司',
        '中万.网络',
        '中万.cn',
    ]

    for domain in domain_list:
        # print(parse_whois_raw(get_whois_raw(domain, ROOT_SERVER)))
        print(whois_util.get_domain_info(domain))
