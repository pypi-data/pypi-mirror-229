# -*- coding: utf-8 -*-
import json
from datetime import datetime

from peewee import IntegerField, DateTimeField, TextField, AutoField

from domain_admin.enums.event_enum import EventEnum
from domain_admin.enums.notify_type_enum import NotifyTypeEnum
from domain_admin.enums.status_enum import StatusEnum
from domain_admin.model.base_model import BaseModel


class NotifyModel(BaseModel):
    """通知配置"""
    id = AutoField(primary_key=True)

    # 用户id
    user_id = IntegerField(null=False)

    # 事件分类
    event_id = IntegerField(null=False, default=EventEnum.SSL_CERT_EXPIRE)

    # 分类
    type_id = IntegerField(null=False, default=NotifyTypeEnum.Unknown)

    # 值
    value_raw = TextField(default=None, null=True)

    # 分类
    status = IntegerField(null=False, default=StatusEnum.Enabled)

    # 创建时间
    create_time = DateTimeField(default=datetime.now)

    # 更新时间
    update_time = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'tb_notify'

        indexes = (
            # 唯一索引
            (('user_id', 'type_id'), True),
        )

    @property
    def value(self):
        if self.value_raw:
            return json.loads(self.value_raw)
        else:
            return None
