# -*- coding: utf-8 -*-
# @Time    : 2018/9/12 下午3:25
# @Author  : jiangchao
import unittest

import ddt
from ForInterface.Public.Logs import LOG
from ForInterface.requestutils.testFengzhuang import TestApi
from ForInterface.Public.get_excel import makedata
from ForInterface.Public.panduan import expectJson

casename = 'login'
data_test = makedata(casename)


@ddt.ddt
class Weibotest(unittest.TestCase):
    '''微博登录'''

    @ddt.data(*data_test)
    def test_WeiboSearch(self, data_test):
        LOG.info(data_test['name'])
        apijson = TestApi(data_test['url'], data_test['parem'], data_test['fangshi']).getJson()
        self.assertEqual(True, expectJson(data_test['qiwang'], apijson))
