import unittest
import ddt
from testcase.userservice import host,curpath
from util.Log import LOG
from util.load_testcases import makedata
from util.request_util import TestApi
from util.assert_util import expectJson, checkSqlData
casename='checkPhoneCode'
data_test = makedata(casename,curpath)
@ddt.ddt
class checkPhoneCodeTest(unittest.TestCase):
    '''checkPhoneCode，校验短信验证码'''
    @ddt.data(*data_test)
    def test_checkPhoneCode(self, data_test):
        LOG.info(data_test['name'])
        apijson = TestApi(host, data_test['url'], data_test['param'], data_test['type'], data_test['method']).getJson()
        self.assertEqual(True, expectJson(data_test['expect'], apijson))