import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))
class Config:
      ad="ad主机IP"
      ad_my_base = "OU=xxx,DC=xxx,DC=xxx"
      ad_admin = "xxx\\xxx"
      ad_adminpwd = "xxx"
      ad_port = 636
      use_ssl=True
REDIS_URL = "redis://xxxx:6379/0"
KEY = "xxxx" #url 加密码操作
SECRET_KEY="xxx" #csrf token 加密码字符串
mailserver="邮件服务器地址"
mail_port="邮件服务端口"
mail_use_tls=False
mail_use_ssl=True
mail_username="邮箱账号"
mail_password="邮箱密码"
ACCESS_KEY_ID = "啊里短信接ID"
ACCESS_KEY_SECRET = "啊里短信key_secret"
