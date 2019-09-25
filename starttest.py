# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest
from util import create_report
from util import control_util
from util import db_operate
from util.send_email import sendemail


if __name__ == '__main__':
    #本地全量调试需要注释掉下面代码并给对应参数赋值
    # service,branch = control_util.importparam(sys.argv[1:])
    service, branch=['userservice'],['用户服务']
    for (servicename,branchname) in zip(service,branch):
        suite = unittest.TestSuite()
        runpath = control_util.basepath+"/testcase/" + servicename
        # db_operate.deletedata(runpath)
        # db_operate.restore(runpath)
        suite.addTests(unittest.TestLoader().discover(start_dir=runpath, pattern="*_Case.py"))
        now = time.strftime("%m%d%H%M", time.localtime(time.time()))
        attachname = servicename + branchname + str(now) + '.html'
        file_dir = os.path.join(control_util.basepath, 'testreport')
        file = os.path.join(file_dir, (servicename + branchname + now + '.html'))
        re_open = open(file, 'wb')
        runner = create_report.BSTestRunner(stream=re_open, title=(servicename) + "服务", description='测试分支：' + branchname)
        filepath1 = os.path.join(control_util.basepath + '/testreport/%s' % attachname)
        testcount = suite.countTestCases()
        print('测试用例共：', testcount, '条')
        runner.run(suite)
        # db_operate.dbbackup(runpath)
        sendemail(filepath1, attachname, servicename,runpath)