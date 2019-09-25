# -*- coding: utf-8 -*-
# @Time    : 2019/4/8 2:04 PM
# @Author  : jiangchao
import socket
import telnetlib
import requests,json
from util.Log import LOG
from util.control_util import formatparam


class TestApi(object):
    def __init__(self, host,url, param, requesttype, method):
        if 'html' in param:
            self.url = 'https://' + 'chaoaicai.com' + '/' + url
        if 'bo' not in requesttype:
            self.url = 'http://'+host+'/' +url
            if param == None:
                param = ''
        else:
            self.host = host
            self.url = url
        self.param = param
        self.requesttype = requesttype
        self.method = method
    def testapi(self):
        if self.requesttype == 'POST' or self.requesttype=='post':
            resp = requ().post(self.url, self.param)
        elif self.requesttype == "GET" or self.requesttype=='get':
            resp = requ().get(self.url, self.param)
        else:
            resp = requ().dubborequest(self.host, self.url,self.param,self.method)
        if resp == {}:
            print('请求数据：' + self.url + '?' +self.param)
            resp = {"returnCode": "9999", "returnMessage": "没有返回值！"}
        return resp

    def getJson(self):
        json_data = self.testapi()
        return json_data




class requ():
    def __init__(self):
        self.headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent":"Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"}


    # get请求
    def get(self, url, params):
        try:
            r = requests.get(url, params=params, headers=self.headers)
            r.encoding = 'UTF-8'
            json_response = json.loads(r.text)
            return json_response
        except Exception as e:
            LOG.info('get请求出错，出错原因:%s'%e)
            print('get请求出错,出错原因:%s'%e)
            return {}

    # post请求
    def post(self, url, params):
        try:
            r =requests.post(url, data=params, verify=False, headers=self.headers)
            print('接口响应时间：', r.elapsed.microseconds / 1000, 'ms')
            print('请求数据：'+url+'\n'+params)
            if r.status_code != 200:
                return {"Http请求": "请求失败", "ResponsStatus": r.status_code}
            str = r.text
            #后续更改为更通用规则，暂时如此
            if 'chaxun(' in str:
                str= str[7:(len(str)-1)]
            json_response = json.loads(str)
            return json_response
        except:
            return {}
    #Dubbo请求
    def dubborequest(self, host, interface, param, method):
        print('服务器地址:' + host + '\n' + 'interface:' + interface + '\n' + 'method:' + method + '\n' + 'param:' + param)
        host = host.split(':')
        conn = Dubbo(host[0], host[1])
        result = conn.invoke(
            interface,
            method,
            param
        )
        return result


class Dubbo(telnetlib.Telnet):

    prompt = 'dubbo>'
    coding = 'gbk'

    def __init__(self, host=None, port=0,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        #通过调调用父类中初始化方法获取通服务器的链接
        # if host is not None:
        #     self.open(host, port, timeout)
        super().__init__(host, port)
        self.write(b'\n')
    #封装命令行执行并返回对应内容
    def command(self, flag, str_=""):
        data = self.read_until(flag.encode())
        self.write(str_.encode(self.coding) + b"\n")
        # print(data)
        return data
    #通过获取所需参数拼接出需要执行的命令，通过已经定义的请求类型执行
    def invoke(self, service_name, method_name, arg):

        if arg == ' ':
            command_str = "invoke {0}.{1}".format(
                service_name, method_name)+'()'
        else:
            arg = formatparam(arg)
            command_str = "invoke {0}.{1}({2})".format(
                service_name, method_name, arg)
            print(command_str)
        self.command(Dubbo.prompt, command_str)
        data = self.command(Dubbo.prompt, "")
        #序列化返回结果
        try:
            data = json.loads(data.decode(Dubbo.coding,
                                      errors='ignore').split('\n')[0].strip())
        except:
            data = data.decode(Dubbo.coding,
                                      errors='ignore')
        return data


# if __name__ == '__main__':
#     data = requ().dubborequest('172.16.21.235:7062', 'com.tritonsfs.cac.depository.service.UserService',"{},'172.16.22.82'",'register')
    # print(data)



