# -*- coding: utf-8 -*-
import math
from datetime import datetime

from peewee import IntegerField, DateTimeField, BooleanField, TextField, AutoField

from domain_admin.model.base_model import BaseModel
from domain_admin.utils import datetime_util


class LogSchedulerModel(BaseModel):
    """日志"""
    id = AutoField(primary_key=True)

    # 状态
    status = BooleanField(default=False)

    # 错误信息
    error_message = TextField(default='')

    # 创建时间
    create_time = DateTimeField(default=datetime.now)

    # 更新时间
    update_time = DateTimeField(default=None, null=True)

    class Meta:
        table_name = 'log_scheduler'

    @property
    def total_time(self):
        if isinstance(self.update_time, datetime) and isinstance(self.create_time, datetime):
            return math.ceil(self.update_time.timestamp() - self.create_time.timestamp())

    @property
    def total_time_label(self):
        if self.total_time:
            return datetime_util.seconds_for_human(self.total_time)
