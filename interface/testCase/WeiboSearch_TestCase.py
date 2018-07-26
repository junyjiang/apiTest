import unittest

import ddt
from interface.Public.Log import LOG
from interface.Interface.testFengzhuang import TestApi
from interface.Public.get_excel import makedata
from interface.Public.panduan import expectJson

casename = 'login'
data_test = makedata(casename)
@ddt.ddt
class WeiboSearchtest(unittest.TestCase):
    '''微博登录'''
    @ddt.data(*data_test)
    def testWeiboSearch(self,data_test):
        LOG.info(data_test['name'])
        apijson = TestApi(data_test['url'], data_test['parem'], data_test['fangshi']).getJson()
        self.assertEqual(True, expectJson(data_test['qiwang'], apijson))


