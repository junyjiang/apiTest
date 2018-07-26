# -*- coding: utf-8 -*-
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml
def load_email_setting():  # 从配置文件中加载获取email的相关信息
    data_file = open(r"../config/email.yaml", encoding='UTF-8')
    datas = yaml.load(data_file)
    data_file.close()
    return (datas['foremail'], datas['password'], datas['toeamil'], datas['title'])

def sendemail1(filepath1):  # 发送email
    sender, password, mail_to, mail_body = load_email_setting()
    msg = MIMEMultipart()
    msg['Subject'] = '接口自动化测试报告'
    msg['From'] = '接口自动化测试平台'
    msg['To'] = ",".join(mail_to)
    msg['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
    att1 = MIMEText(open(r'%s' % filepath1, 'rb').read(), 'html', 'utf-8')
    att = MIMEText(open(r'%s' % filepath1, 'rb').read(), 'html', 'utf-8')
    att["Content-Type"] = 'application/octet-stream'
    att["Content-Disposition"] = 'attachment; filename="TestReport.html"'
    txt = MIMEText("这是接口自动化测试报告的邮件，详情见附件", 'plain', 'utf-8')
    # msg.attach(txt)
    msg.attach(att1)
    msg.attach(att)
    smtp = smtplib.SMTP()
    server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)
    server.login(sender, password)
    server.sendmail(sender, mail_to, msg.as_string())
    server.quit()
