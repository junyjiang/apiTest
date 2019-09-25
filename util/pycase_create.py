# -*- coding: utf-8 -*-
# @Time    : 2019/4/28 10:08 AM
# @Author  : jiangchao
from util.load_testcases import getcasename

def createpycase(path,servicename):
    apinamelist,casenamelist = getcasename(path)
    for (apiname,casename) in zip(apinamelist,casenamelist):
        f = open(path+"/"+apiname+"_Case"+".py", "w")
        f.write("import unittest\
\nimport ddt\
\nfrom testcase."+servicename+" import host,curpath\
\nfrom util.Log import LOG\
\nfrom util.load_testcases import makedata\
\nfrom util.request_util import TestApi\
\nfrom util.assert_util import expectJson, checkSqlData\
\ncasename="+"'"+apiname+"'"+"\
\ndata_test = makedata(casename,curpath)\
\n@ddt.ddt\
\nclass "+apiname+"Test(unittest.TestCase):\
\n    "+"'''"+apiname +"，"+casename+"'''"+"\
\n    @ddt.data(*data_test)\
\n    def test_"+apiname+"(self, data_test):\
\n        LOG.info(data_test['name'])\
\n        apijson = TestApi(host, data_test['url'], data_test['param'], data_test['type'], data_test['method']).getJson()\
\n        self.assertEqual(True, expectJson(data_test['expect'], apijson))")