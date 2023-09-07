# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler

from peewee import Model, SqliteDatabase, MySQLDatabase
from playhouse.db_url import connect
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.sqliteq import SqliteQueueDatabase

from domain_admin.config import SQLITE_DATABASE_PATH, DB_CONNECT_URL

# 打印日志
from domain_admin.service.file_service import resolve_log_file

logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.addHandler(logging.FileHandler(resolve_log_file("peewee.log")))

# 单个日志文件最大为1M
handler = RotatingFileHandler(resolve_log_file("peewee.log"), maxBytes=1024 * 1024 * 1, encoding='utf-8')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# 多线程写入方式，会造成读取不到刚写入的数据
# db = connect(SQLITE_DATABASE_URL)
# db = SqliteQueueDatabase(database=SQLITE_DATABASE_PATH)
# db = SqliteExtDatabase(database=SQLITE_DATABASE_PATH)
# db = SqliteDatabase(database=SQLITE_DATABASE_PATH)

db = connect(url=DB_CONNECT_URL)


class BaseModel(Model):
    class Meta:
        database = db
