# -*- coding: utf-8 -*-
import requests, json
from ForInterface.Public.Logs import LOG


# @logger('requests封装')
class requ():
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; ZUK Z2131 Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.134 Mobile Safari/537.36"}  # {"User-Agent":"Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"}

    # get请求
    def get(self, url, params):
        try:
            print('请求数据：' + url + params)
            r = requests.get(url, params)
            r.encoding = 'UTF-8'
            json_response = json.loads(r.text)
            return json_response
        except Exception as e:
            LOG.info('get请求出错，出错原因:%s' % e)
            print('get请求出错,出错原因:%s' % e)
            return {}

    # post请求
    def post(self, url, params):
        try:
            r = requests.post(url, params=params, verify=False)
            print('接口响应时间：', r.elapsed.microseconds / 1000, 'ms')
            print('请求数据：' + url + '?' + params)
            if r.status_code != 200:
                return {"Http请求": "请求失败", "ResponsStatus": r.status_code}
            str = r.text
            # 后续更改为更通用规则，暂时如此(根据需求获取json)
            # if 'chaxun(' in str:
            #     str= str[7:(len(str)-1)]
            json_response = json.loads(str)
            return json_response
        except:
            return {}

    def delfile(self, url, params):  # 删除的请求
        try:
            del_word = requests.delete(url, params, headers=self.headers)
            json_response = json.loads(del_word.text)
            return json_response
        except Exception as e:
            LOG.info('del请求出错，出错原因:%s' % e)
            print('del请求出错,原因:%s' % e)
            return {}

    def putfile(self, url, params):  # put请求
        try:
            data = json.dumps(params)
            me = requests.put(url, data)
            json_response = json.loads(me.text)
            return json_response
        except Exception as e:
            LOG.info('put请求出错，出错原因:%s' % e)
            print('put请求出错,原因:%s' % e)
