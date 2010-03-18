#coding=utf-8
from google.appengine.api import users
#一个分页的最多项数
PAGE_COUNT=6

LOGOUT = users.create_logout_url('/login')
LOGIN = users.create_login_url('/login')
CURUSER = users.get_current_user()


#要导入数据库的数据文件
IMPORT_FILE = "../../import/data.json"

