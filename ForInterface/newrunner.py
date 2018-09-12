# -*- coding: utf-8 -*-
import os
import time
import unittest
from ForInterface.Public.Suite import Suite
# 集成jenkins后路径
from ForInterface.Public import BSTestRunner
from ForInterface.Public.emmail import sendemail1
from ForInterface.testCase.WeiboCase import Weibotest

if __name__ == '__main__':
    suite = Suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Weibotest))
    now = time.strftime("%Y%m%d%H%M", time.localtime(time.time()))
    basedir = os.path.abspath(os.path.dirname(__file__))
    file_dir = os.path.join(basedir, 'test_Report')
    file = os.path.join(file_dir, (now + '-result.html'))
    re_open = open(file, 'wb')
    runner = BSTestRunner.BSTestRunner(stream=re_open, title='接口测试报告', description='测试报告详情')
    basdir = os.path.abspath(os.path.dirname(__file__))
    filepath1 = os.path.join(basdir + '/test_Report/%s-result.html' % now)
    testcount = suite.countTestCases()
    print('测试用例共：', testcount, '条')
    runner.run(suite)
    # sendemail1(filepath1)
