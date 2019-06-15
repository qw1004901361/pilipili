# coding=UTF-8
# 数据库连接
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://qw:qw@971230@134.175.93.183:3306/pilipili"
# SQLALCHEMY_DATABASE_URI = "mysql+pymysql://qw:qw@971230@localhost:3306/pilipili"
SQLALCHEMY_TRACK_MODIFICATIONS = True
# Redis配置
REDIS_URL = "redis://127.0.0.1:6379/0"
# 密钥
SECRET_KEY = r"\x88D\xf09\x6\xa0A\x7\xc5V\xbe\x8b\xef\xd7\xd8\xd3\xe6\x98*4\x22\x123"
# APScheduler
SCHEDULER_API_ENABLED = True

# # Email 配置
# # MAIL_SERVER = 'smtp.exmail.qq.com'
# MAIL_DEBUG = True
# MAIL_SERVER = 'smtp.qq.com'
# MAIL_PORT = 465
# MAIL_USE_SSL = True
# MAIL_USE_TSL = False
# MAIL_USERNAME = '1004901361@qq.com'
# MAIL_PASSWORD = 'lnlstpdwzyzdbfdg'
# # MAIL_SUBJECT_PREFIX = '[鱼书]'
# MAIL_SENDER = '鱼书 <hello@yushu.im>'
