# -*- coding: utf-8 -*-
from ForInterface.requestutils.test_requests import requ
from ForInterface.config.account import *

reques = requ()
# @logger("开始请求")
baseUrl = BaseUrl


class TestApi(object):
    def __init__(self, url, parem, fangshi):
        self.url = baseUrl + url
        if parem == None:
            parem = ''
        self.parem = parem
        self.fangshi = fangshi

    def testapi(self):
        resp = {}
        if self.fangshi == 'POST' or self.fangshi == 'post':
            resp = reques.post(self.url, self.parem)
        elif self.fangshi == 'GET' or self.fangshi == 'get':
            resp = reques.get(self.url, self.parem)
        # 当返回为空时自定义返回结果，以便校验
        if resp == {}:
            resp = {"returnCode": "9999", "returnMessage": "没有返回值！"}
        return resp

    def getJson(self):
        json_data = self.testapi()
        return json_data
