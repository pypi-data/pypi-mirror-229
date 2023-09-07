# -*- coding: utf-8 -*-
"""
domain_service.py
"""
import time
import traceback
import warnings
from datetime import datetime
from typing import List

from peewee import chunked
from playhouse.shortcuts import model_to_dict

from domain_admin.log import logger
from domain_admin.model.address_model import AddressModel
from domain_admin.model.domain_model import DomainModel
from domain_admin.model.group_model import GroupModel
from domain_admin.model.log_scheduler_model import LogSchedulerModel
from domain_admin.model.user_model import UserModel
from domain_admin.service import email_service, render_service, global_data_service, cache_domain_info_service
from domain_admin.service import file_service
from domain_admin.service import notify_service
from domain_admin.service import system_service
from domain_admin.utils import datetime_util, cert_util, whois_util, file_util, time_util
from domain_admin.utils import domain_util
from domain_admin.utils.cert_util import cert_common, cert_socket_v2
from domain_admin.utils.flask_ext.app_exception import AppException, ForbiddenAppException


def update_domain_info(domain_row: DomainModel):
    """
    更新域名信息
    :param row:
    :return:
    """
    # logger.info("%s", model_to_dict(domain_row))

    # 获取域名信息
    domain_info = None

    err = ''

    try:
        domain_info = cache_domain_info_service.get_domain_info(domain_row.domain)
    except Exception as e:
        err = e.__str__()
        pass

    update_data = {
        'domain_start_time': None,
        "domain_expire_time": None,
        'domain_expire_days': 0,
    }

    if domain_info:
        update_data = {
            'domain_start_time': domain_info.domain_start_time,
            "domain_expire_time": domain_info.domain_expire_time,
            'domain_expire_days': domain_info.domain_expire_days,
        }

    DomainModel.update(
        **update_data,
        domain_check_time=datetime_util.get_datetime(),
        update_time=datetime_util.get_datetime(),
    ).where(
        DomainModel.id == domain_row.id
    ).execute()

    return err


def update_ip_info(row: DomainModel):
    """
    更新ip信息
    :param row:
    :return:
    """
    # 获取ip地址
    domain_ip = ''

    try:
        domain_ip = cert_common.get_domain_ip(row.domain)
    except Exception as e:
        pass

    DomainModel.update(
        ip=domain_ip,
        ip_check_time=datetime_util.get_datetime(),
        update_time=datetime_util.get_datetime(),
    ).where(
        DomainModel.id == row.id
    ).execute()


def update_domain_host_list(domain_row: DomainModel):
    """
    更新ip信息
    :param row:
    :return:
    @since v1.2.24
    """
    domain_host_list = []

    try:
        domain_host_list = cert_socket_v2.get_domain_host_list(
            domain=domain_row.domain,
            port=domain_row.port
        )
    except Exception as e:
        pass

    lst = [
        {
            'domain_id': domain_row.id,
            'host': domain_host
        } for domain_host in domain_host_list]

    logger.info(lst)

    AddressModel.insert_many(lst).on_conflict_ignore().execute()


def update_domain_address_list_cert(domain_row: DomainModel):
    """
    更新证书信息
    :return:
    """
    # logger.info("%s", model_to_dict(domain_row))

    lst = AddressModel.select().where(
        AddressModel.domain_id == domain_row.id
    )

    err = ''
    for address_row in lst:
        err = update_address_row_info(address_row, domain_row)

    sync_address_info_to_domain_info(domain_row)
    return err


def update_address_row_info(address_row, domain_row):
    """
    更新单个地址信息
    :param domain_row:
    :param address_row:
    :return:
    """

    # 获取证书信息
    cert_info = {}

    err = ''
    try:
        cert_info = cert_socket_v2.get_ssl_cert_info(
            domain=domain_row.domain,
            host=address_row.host,
            port=domain_row.port
        )
    except Exception as e:
        err = e.__str__()
        logger.error(traceback.format_exc())

    address = AddressModel()
    address.ssl_start_time = cert_info.get('start_date')
    address.ssl_expire_time = cert_info.get('expire_date')

    AddressModel.update(
        ssl_start_time=address.ssl_start_time,
        ssl_expire_time=address.ssl_expire_time,
        ssl_expire_days=address.real_time_ssl_expire_days,
        # ssl_check_time=datetime_util.get_datetime(),
        update_time=datetime_util.get_datetime(),
    ).where(
        AddressModel.id == address_row.id
    ).execute()

    return err


def update_address_row_info_with_sync_domain_row(address_id: int):
    """
    更新主机信息并同步到与名表
    :param address_id:
    :return:
    """
    address_row = AddressModel.get_by_id(address_id)

    domain_row = DomainModel.get_by_id(address_row.domain_id)

    update_address_row_info(address_row, domain_row)

    sync_address_info_to_domain_info(domain_row)


def sync_address_info_to_domain_info(domain_row: DomainModel):
    """
    同步主机信息到域名信息表
    :return:
    """
    first_address_row = AddressModel.select().where(
        AddressModel.domain_id == domain_row.id
    ).order_by(
        AddressModel.ssl_expire_days.asc()
    ).first()

    connect_status = False

    if first_address_row is None:
        first_address_row = AddressModel()
        first_address_row.ssl_start_time = None
        first_address_row.ssl_expire_time = None

    elif first_address_row.real_time_ssl_expire_days > 0:
        connect_status = True

    DomainModel.update(
        start_time=first_address_row.ssl_start_time,
        expire_time=first_address_row.ssl_expire_time,
        expire_days=first_address_row.real_time_ssl_expire_days,
        connect_status=connect_status,
        update_time=datetime_util.get_datetime(),
    ).where(
        DomainModel.id == domain_row.id
    ).execute()


def update_cert_info(row: DomainModel):
    """
    更新证书信息
    :param row:
    :return:
    """
    # 获取证书信息
    cert_info = {}

    try:
        cert_info = get_cert_info(row.domain)
    except Exception as e:
        pass

    DomainModel.update(
        start_time=cert_info.get('start_date'),
        expire_time=cert_info.get('expire_date'),
        expire_days=cert_info.get('expire_days', 0),
        total_days=cert_info.get('total_days', 0),
        # ip=cert_info.get('ip', ''),
        connect_status=cert_info.get('connect_status'),
        # detail_raw="",
        check_time=datetime_util.get_datetime(),
        update_time=datetime_util.get_datetime(),
    ).where(
        DomainModel.id == row.id
    ).execute()


def update_domain_row(domain_row: DomainModel):
    """
    更新域名相关数据
    :param domain_row:
    :return:
    """
    # fix old data update root domain
    if not domain_row.root_domain:
        DomainModel.update(
            root_domain=domain_util.get_root_domain(domain_row.domain)
        ).where(
            DomainModel.id == domain_row.id
        ).execute()

    # 动态主机ip，需要先删除所有主机地址
    if domain_row.is_dynamic_host:
        AddressModel.delete().where(
            AddressModel.domain_id == domain_row.id
        ).execute()

    # 主机ip信息
    update_domain_host_list(domain_row)

    # 证书信息
    update_domain_address_list_cert(domain_row)


def get_cert_info(domain: str):
    now = datetime.now()
    info = {}
    expire_days = 0
    total_days = 0
    connect_status = True

    try:
        info = cert_util.get_cert_info(domain)

    except Exception:
        logger.error(traceback.format_exc())
        connect_status = False

    start_date = info.get('start_date')
    expire_date = info.get('expire_date')

    if start_date and expire_date:
        start_time = datetime_util.parse_datetime(start_date)
        expire_time = datetime_util.parse_datetime(expire_date)

        expire_days = (expire_time - now).days
        total_days = (expire_time - start_time).days

    return {
        'start_date': start_date,
        'expire_date': expire_date,
        'expire_days': expire_days,
        'total_days': total_days,
        'connect_status': connect_status,
        # 'ip': info.get('ip', ''),
        'info': info,
    }


def get_domain_info(domain: str):
    """
    获取域名注册信息
    :param domain: 域名
    :param cache: 查询缓存字典
    :return:
    """
    warnings.warn("use cache_domain_info_service.get_domain_info", DeprecationWarning)

    # cache = global_data_service.get_value('update_domain_list_info_cache')

    now = datetime.now()

    # 获取域名信息
    domain_info = {}
    domain_expire_days = 0

    # 解析出域名和顶级后缀
    extract_result = domain_util.extract_domain(domain)
    domain_and_suffix = '.'.join([extract_result.domain, extract_result.suffix])

    # if cache:
    #     domain_info = cache.get(domain_and_suffix)

    if not domain_info:
        try:
            domain_info = whois_util.get_domain_info(domain_and_suffix)
            # if cache:
            #     cache[domain_and_suffix] = domain_info

        except Exception:
            logger.error(traceback.format_exc())

    domain_start_time = domain_info.get('start_time')
    domain_expire_time = domain_info.get('expire_time')

    if domain_expire_time:
        domain_expire_days = (domain_expire_time - now).days

    return {
        'start_time': domain_start_time,
        'expire_time': domain_expire_time,
        'expire_days': domain_expire_days
    }


def update_all_domain_cert_info():
    """
    更新所有域名信息
    :return:
    """
    rows = DomainModel.select().where(
        DomainModel.auto_update == True
    ).order_by(DomainModel.expire_days.asc())

    for row in rows:
        update_domain_row(row)


def update_all_domain_cert_info_of_user(user_id):
    """
    更新用户的所有证书信息
    :return:
    """
    rows = DomainModel.select().where(
        DomainModel.user_id == user_id,
        DomainModel.auto_update == True
    )

    for row in rows:
        update_domain_row(row)

    # key = f'update_domain_status:{user_id}'
    # global_data_service.set_value(key, False)


def get_domain_info_list(user_id=None):
    query = DomainModel.select()

    user_row = UserModel.get_by_id(user_id)

    query = query.where(
        DomainModel.user_id == user_id,
        DomainModel.is_monitor == True,
        DomainModel.expire_days < user_row.before_expire_days
    )

    query = query.order_by(
        DomainModel.expire_days.asc(),
        DomainModel.id.desc()
    )

    lst = list(map(lambda m: model_to_dict(
        model=m,
        # exclude=[DomainModel.detail_raw],
        extra_attrs=[
            'start_date',
            'expire_date',
            # 'real_time_domain_expire_days',
            'real_time_expire_days',
            # 'expire_days',
        ]
    ), query))

    # def compare(a, b):
    #     if a['expire_days'] and b['expire_days']:
    #         return a['expire_days'] - b['expire_days']
    #     else:
    #         if a['expire_days']:
    #             return a['expire_days']
    #         else:
    #             return -b['expire_days']

    # lst = sorted(lst, key=cmp_to_key(compare))

    return lst


def check_domain_cert(user_id):
    """
    查询域名证书到期情况
    :return:
    """
    user_row = UserModel.get_by_id(user_id)

    # lst = get_domain_info_list(user_id)

    rows = DomainModel.select().where(
        DomainModel.user_id == user_id,
        DomainModel.is_monitor == True,
        DomainModel.expire_days <= user_row.before_expire_days
    ).order_by(
        DomainModel.expire_days.asc(),
        DomainModel.id.desc()
    )

    lst = [model_to_dict(
        model=row,
        extra_attrs=[
            'start_date',
            'expire_date',
            'real_time_expire_days',
        ]
    ) for row in rows]

    if len(lst) > 0:
        notify_user(user_id, lst)
        # send_domain_list_email(user_id)


def update_and_check_all_cert():
    """
    更新并检查所域名信息和证书信息
    :return:
    """

    # 更新全部域名证书信息
    update_all_domain_cert_info()

    # 全员检查并发送用户通知
    # if status:
    user_rows = UserModel.select()

    for row in user_rows:
        # 内层捕获单个用户发送错误
        check_domain_cert(row.id)


def send_domain_list_email(user_id, rows: List[DomainModel]):
    """
    发送域名信息
    :param user_id:
    :return:
    """

    # 配置检查
    config = system_service.get_system_config()

    system_service.check_email_config(config)

    email_list = notify_service.get_notify_email_list_of_user(user_id)

    if not email_list:
        raise AppException('收件邮箱未设置')

    # lst = get_domain_info_list(user_id)

    content = render_service.render_template('cert-email.html', {'list': rows})

    email_service.send_email(
        subject='[Domain Admin]证书过期提醒',
        content=content,
        to_addresses=email_list,
        content_type='html'
    )


def check_permission_and_get_row(domain_id, user_id):
    """
    权限检查
    :param domain_id:
    :param user_id:
    :return:
    """
    row = DomainModel.get_by_id(domain_id)
    if row.user_id != user_id:
        raise ForbiddenAppException()

    return row


def add_domain_from_file(filename, user_id):
    logger.info('user_id: %s, filename: %s', user_id, filename)

    lst = domain_util.parse_domain_from_file(filename)

    lst = [
        {
            'domain': item.domain,
            'root_domain': item.root_domain,
            'port': item.port,
            'alias': item.alias,
            'user_id': user_id,
        } for item in lst
    ]

    for batch in chunked(lst, 500):
        DomainModel.insert_many(batch).on_conflict_ignore().execute()


def export_domain_to_file(user_id):
    """
    导出域名到文件
    :param user_id:
    :return:
    """
    # 域名数据
    rows = DomainModel.select().where(
        DomainModel.user_id == user_id
    ).order_by(
        DomainModel.expire_days.asc(),
        DomainModel.id.desc(),
    )

    #  分组数据
    group_rows = GroupModel.select().where(
        GroupModel.user_id == user_id
    )

    group_map = {row.id: row.name for row in group_rows}

    lst = []
    for row in list(rows):
        row.group_name = group_map.get(row.group_id, '')
        lst.append(row)

    content = render_service.render_template('cert-export.csv', {'list': lst})

    filename = datetime.now().strftime("cert_%Y%m%d%H%M%S") + '.csv'

    temp_filename = file_service.resolve_temp_file(filename)
    # print(temp_filename)
    with open(temp_filename, 'w') as f:
        f.write(content)

    return filename


def notify_user(user_id, rows: List[DomainModel]):
    """
    尝试通知用户
    :param user_id:
    :return:
    """
    try:
        send_domain_list_email(user_id, rows)
    except Exception as e:
        logger.error(traceback.format_exc())

    try:
        notify_service.notify_webhook_of_user(user_id)
    except Exception as e:
        logger.error(traceback.format_exc())


def update_and_check_domain_cert(user_id):
    # 先更新，再检查
    # update_all_domain_cert_info_of_user(user_id)

    check_domain_cert(user_id)

    # key = f'check_domain_status:{user_id}'
    # global_data_service.set_value(key, False)
