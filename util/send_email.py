# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 9:51
# @Author  : jiangchao
import smtplib
import time
import socket
import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from util.control_util import basepath


def load_email_setting(servicename):  # 从配置文件中加载获取email的相关信息
    data_file = open(basepath+"/testcase/"+servicename+"/conf/email_list.yaml",
                     encoding='UTF-8')
    datas = yaml.load(data_file)
    data_file.close()
    return (datas['foremail'], datas['password'], datas['toeamil'], datas['title'])


def sendemail(filepath1,  attachname,servicename,path):  # 发送email
    sock = socket.socket()
    sock.setblocking(False)
    sender, password, mail_to, mail_body = load_email_setting(servicename)
    msg = MIMEMultipart()
    msg['Subject'] = '接口自动化测试报告'
    msg['From'] = 'CAC接口自动化测试平台'
    msg['To'] = ",".join(mail_to)
    msg['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
    att1 = MIMEText(open(r'%s' % filepath1, 'rb').read(), 'html', 'utf-8')
    # att2 = MIMEText(open(path+'/database/backupdatabase.zip', 'rb').read(), 'base64', 'utf-8')
    att = MIMEText(open(r'%s' % filepath1, 'rb').read(), 'html', 'utf-8')
    att["Content-Type"] = 'application/octet-stream'
    # att2.add_header('Content-Disposition', 'attachment', filename='database.zip')
    att.add_header('Content-Disposition', 'attachment', filename=attachname)
    msg.attach(att1)
    # msg.attach(att2)
    msg.attach(att)
    server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)
    server.login(sender, password)
    server.sendmail(sender, mail_to, msg.as_string())
    server.quit()
