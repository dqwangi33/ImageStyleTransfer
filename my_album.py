# coding:utf-8
#展示图像
import sys
import os
from flask import session

# 一个文件夹下的图片文件
def getFiles(filepath):
  files = []
  if os.path.isdir(filepath):
    for file in os.listdir(filepath):
      if os.path.isdir(file):
        getFiles(file)
      elif file.endswith('.jpg') or file.endswith('.png') or file.endswith('.gif'):
        files.append(filepath + str(file))
  elif os.path.isfile(filepath):
    files.append(filepath)
  return files
 
 
# 获取给定目录下所有以.jpg .png .gif结尾的文件，并补全路径保存到列表中输出
def recourse(filepath):
  files = []
  for fpathe, dirs, fs in os.walk(filepath):
    for f in fs:
      if f.endswith('.jpg') or f.endswith('.png') or f.endswith('.gif'):
        files.append(os.path.join('../static/img/generated/'+session["user_name"], f))
  return files
 
 
# 生成网页源码文件，指定
def generate(files, shuffle=False):
  template_start = '''
  <html><head><meta charset='utf-8'><title>网页版相册</title><link rel="stylesheet" type="text/css" href="csshake-slow.min.css">
  <link rel="stylesheet" type="text/css" href="http://csshake.surge.sh/csshake-slow.min.css"></script></head><body>
  '''
  template_body = ''
  # 如果指定乱序，就乱序列表中的数据
  if shuffle == True:
    from random import shuffle
    shuffle(files)
  for file in files:
    template_body += '<a href="' + file + '"><img class="shake-slow" src="' + file + '" style="margin-left:15px;margin-top:15px;width:auto;height:250px;"></a>'
 
  template_end = '''
  </body></html>
 '''
  html = template_start + template_body + template_end
  return html
 
# 生成html文件，并输出到指定的目录
def write2File(filepath, data):
  file = open(filepath, 'wb')
  file.write(data)
  file.close()


 
