# -*- coding: utf-8 -*-
import json
from datetime import datetime
import warnings
from domain_admin.config import ADMIN_USERNAME, ADMIN_PASSWORD, DEFAULT_BEFORE_EXPIRE_DAYS
from domain_admin.model.base_model import BaseModel
from peewee import CharField, IntegerField, DateTimeField, BooleanField, TextField, AutoField

from domain_admin.utils import bcrypt_util


class UserModel(BaseModel):
    """用户"""
    id = AutoField(primary_key=True)

    # 用户名
    username = CharField(unique=True, null=None)

    # 密码
    password = CharField()

    # 头像
    avatar_url = CharField(null=None, default='')

    # 过期前多少天提醒
    before_expire_days = IntegerField(null=None, default=DEFAULT_BEFORE_EXPIRE_DAYS)

    # 邮件列表
    # Deprecated 已弃用 v0.0.12
    email_list_raw = TextField(default=None, null=True)

    # 账号状态
    status = BooleanField(default=True)

    # 创建时间
    create_time = DateTimeField(default=datetime.now)

    # 更新时间
    update_time = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'tb_user'

    @property
    def email_list(self):
        warnings.warn("UserModel field email_list is Deprecated, please use NotifyModel", DeprecationWarning)

        if self.email_list_raw:
            return json.loads(self.email_list_raw)
        else:
            return []


def init_table_data():
    data = [
        {
            'username': ADMIN_USERNAME,
            'password': bcrypt_util.encode_password(ADMIN_PASSWORD),
            'before_expire_days': DEFAULT_BEFORE_EXPIRE_DAYS,
        }
    ]

    UserModel.insert_many(data).execute()
