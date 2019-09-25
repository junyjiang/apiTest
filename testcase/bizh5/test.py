import unittest
import ddt
from testcase.bizh5 import host,curpath
from util.Log import LOG
from util.load_testcases import makedata
from util.request_util import TestApi
from util.assert_util import expectJson, checkSqlData
casename='test1'
data_test = makedata(casename,curpath)
@ddt.ddt
class singleSmsTest(unittest.TestCase):
    '''singleSms,单条短信发送'''
    @ddt.data(*data_test)
    def test_singleSms(self, data_test):
        LOG.info(data_test['name'])
        apijson = TestApi(host, data_test['url'], data_test['param'], data_test['type'], data_test['method']).getJson()
        self.assertEqual(True, expectJson(data_test['expect'], apijson))