# -*- coding: utf-8 -*-
"""
@File    : notify_service.py
@Date    : 2022-10-30
@Author  : Peng Shiyu
"""
from typing import List, Optional

import requests

from domain_admin.enums.notify_type_enum import NotifyTypeEnum
from domain_admin.model.notify_model import NotifyModel
from domain_admin.service import domain_service
from domain_admin.utils.flask_ext.app_exception import AppException
from jinja2 import Template


def get_notify_row_value(user_id, type_id):
    """
    获取通知配置
    :param user_id:
    :param type_id:
    :return:
    """
    notify_row = NotifyModel.select().where(
        NotifyModel.user_id == user_id,
        NotifyModel.type_id == type_id
    ).get_or_none()

    if not notify_row:
        return None

    if not notify_row.value:
        return None

    return notify_row.value


def get_notify_email_list_of_user(user_id) -> Optional[List[str]]:
    """
    获取通知配置 - 邮箱列表
    :param user_id:
    :return:
    """
    notify_row_value = get_notify_row_value(user_id, NotifyTypeEnum.Email)

    if not notify_row_value:
        return None

    email_list = notify_row_value.get('email_list')

    if not email_list:
        return None

    return email_list


def get_notify_webhook_row_of_user(user_id):
    """
    获取通知配置 - webhook
    :param user_id:
    :return:
    """
    return get_notify_row_value(user_id, NotifyTypeEnum.WebHook)


def notify_webhook_of_user(user_id):
    """
    通过 webhook 方式通知用户
    :param user_id:
    :return:
    """
    notify_webhook_row = get_notify_webhook_row_of_user(user_id)

    if not notify_webhook_row:
        raise AppException('webhook未设置')

    method = notify_webhook_row.get('method')
    url = notify_webhook_row.get('url')
    headers = notify_webhook_row.get('headers')
    body = notify_webhook_row.get('body')

    if not url:
        raise AppException('url未设置')

    # 支持模板变量
    template = Template(body)
    body_render = template.render(get_template_data(user_id))

    res = requests.request(method=method, url=url, headers=headers, data=body_render.encode('utf-8'))
    res.encoding = res.apparent_encoding

    return res.text


def get_template_data(user_id):
    # 两种参数形式
    domain_list = domain_service.get_domain_info_list(user_id)
    return {
        'domain_list': domain_list
    }
