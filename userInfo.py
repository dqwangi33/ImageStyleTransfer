#coding:utf8
#管理用户信息
from werkzeug.security import check_password_hash

class User:
	def __init__(self,name=None,psw=None,email=None):
		self.name=name
		self.psw=psw
		self.email=email

	def check_psw(self, psw=None):
		return check_password_hash(self.psw,psw)