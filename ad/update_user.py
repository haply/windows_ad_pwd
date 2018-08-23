#coding=utf-8
import sys
sys.path.append("..")
import random
from config import *
from ldap3 import *
admin = Config.ad_admin
adminpwd = Config.ad_adminpwd
def connect_ldap(**kwargs):
    server = Server(host=Config.ad,
                    port=Config.ad_port,
                    use_ssl=Config.use_ssl,
                    connect_timeout=5)
    return Connection(server, raise_exceptions=True, **kwargs)
def check_user(user,password):
    c=connect_ldap(authentication=SIMPLE,user=user,password=password)
    try:
        x=c.bind()
    except:
         return False
    c.unbind()
    return x
def update_password(user_dn,password):
    try:
        c = connect_ldap(authentication=SIMPLE, user=admin, password=adminpwd)
        a=c.bind()
        print(user_dn)
        print(password)
        x = c.extend.microsoft.modify_password(user_dn,password)
        print (x)
        c.unbind()
        return x
    except:
        return False

def get_type(**type):
    c= connect_ldap(authentication=SIMPLE, user=admin,password=adminpwd)
    c.bind()
    for k,v in type.items():
       if "cn" in k:
                   c.search('dc=gtime, dc=com', '(&(objectclass=person)(sAMAccountName='+ v +'))',attributes=['cn','objectclass','mail','telephoneNumber'])
                   try:
                       dn=c.entries[0]
                       mail=dn.mail[0]
                       tel=dn.telephoneNumber[0]
                       use_dn=dn.entry_dn
                       cn=dn.cn
                       c.unbind()
                       return use_dn,mail,tel,cn
                   except:
                       return "not found"
       elif "tel" in k:
                   c.search('dc=gtime, dc=com', '(&(objectclass=person)(telephoneNumber='+ v +'))',attributes=['cn','objectclass','mail','telephoneNumber'])
                   try:
                       dn=c.entries[0]
                       use_dn=dn.entry_dn
                       cn=dn.cn
                       mail=dn.mail[0]
                       c.unbind()
                       return use_dn,mail,cn
                   except:
                       return "not found"
       else:
          c.search('dc=gtime, dc=com', '(&(objectclass=person)(mail='+ v +'))',attributes=['cn','objectclass','mail','telephoneNumber'])
          dn=c.entries[0]
          use_dn=dn.entry_dn
          cn=dn.cn
          mail=dn.mail[0]
          tel=dn.telephoneNumber[0]
          c.unbind()
          return use_dn,mail,cn
def get_sms_token():
    j = 6 
    id = []
    id = ''.join(str(i) for i in random.sample(range(0,9),j))    # sample(seq, n) 从序列seq中选择n个随机且独立的元素；
    return id
if __name__ == '__main__':
   print("run")
