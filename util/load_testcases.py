# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 9:51
# @Author  : jiangchao
import os
import csv
from util.Log import LOG
basedir = os.path.dirname(os.path.dirname(__file__))

def dataimport(casename,path):
    try:
        listmethod = []
        listparam = []
        listurl = []
        listtype = []
        listexpect = []
        listvalue = []
        listname = []
        listSql = []
        with open(path+"/testcase.csv", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # print(list(reader),"\n")
            redata = list(reader)
            relist = []
            for re in redata:
                if re[0]==casename:
                    relist.append(re)
            for i in range(0,len(relist)):
                listname.append(relist[i][1])
                listurl.append(relist[i][2])
                listmethod.append(relist[i][3])
                listparam.append(relist[i][4])
                listtype.append(relist[i][5])
                listexpect.append(relist[i][6])
                listvalue.append(relist[i][7])
                listSql.append(relist[i][8])
        # print(listname, listparam, listurl, listfangshi,
        #             listqiwang,  listvalue, listSql)
        return (listname, listurl, listmethod, listparam, listtype,
                listexpect, listvalue, listSql)
    except FileNotFoundError as e:
        LOG.info('打开测试用例失败，原因是:%s' % e)



# 生成数据驱动所用数据
def makedata(casename,curpath):
    listname, listurl, listmethod, listparam, listtype, listexpect, listvalue, listSql = dataimport(casename,curpath)
    make_data = []
    for i in range(len(listname)):
        make_data.append({'name': listname[i], 'method': listmethod[i],'url': listurl[i], 'param': listparam[i], 'type': listtype[i],
                          'expect': listexpect[i], 'assertdata': listvalue[i],'sql':listSql})
        i += 1
    return make_data

def getcasename(path):
    try:
        listname = []
        listmethodname=[]
        with open(path+"/testcase.csv", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # print(list(reader),"\n")
            redata = list(reader)
            relist = []
            for re in redata:
                relist.append(re)
            for i in range(1,len(relist)):
                try:
                    while relist[i+1][0] !=relist[i][0] and i <= len(relist):
                        listmethodname.append(relist[i][0])
                        listname.append(relist[i][1].split('-')[0])
                        break
                except:
                    listmethodname.append(relist[i][0])
                    listname.append(relist[i][1].split('-')[0])
                # else:
                #     continue
        return (listmethodname,listname)
    except FileNotFoundError as e:
        LOG.info('打开测试用例失败，原因是:%s' % e)

#弃用
# def datacel(casename):
#     try:
#         filepath = basedir+'\\test_Data\\test_data.xlsx'
#         print(filepath)
#         file = openpyxl.load_workbook(filepath)
#         # openpyxl更新到2.5后get_sheet_names@deprecated("Use wb.sheetnames")
#         sheets_names = file.sheetnames
#         listid = []
#         listparem = []
#         listurl = []
#         listfangshi = []
#         listqiwang = []
#         listjsonkey = []
#         listname = []
#         listSql = []
#         for i in range(len(sheets_names)):
#
#             # openpyxl更新到2.5后get_sheet_by_name---- @deprecated("Use wb[sheetname]")
#             sheet = file[sheets_names[i]]
#             rows = sheet.max_row + 1
#             if sheets_names[i] == casename:
#                 for j in range(2, rows):
#                     listid.append(sheet["A" + str(j)].value)
#                     listname.append(sheet["B" + str(j)].value)
#                     listparem.append(sheet["C" + str(j)].value)
#                     listurl.append(sheet["D" + str(j)].value)
#                     listfangshi.append(sheet["E" + str(j)].value)
#                     listqiwang.append(sheet["F" + str(j)].value)
#                     listjsonkey.append(sheet["G" + str(j)].value)
#                     listSql.append(sheet["H" + str(j)].value)
#                 return (listid, listparem, listurl, listfangshi,
#                         listqiwang, listname, listjsonkey, listSql)
#     except FileNotFoundError as e:
#         LOG.info('打开测试用例失败，原因是:%s' % e)
if __name__ == '__main__':
    getcasename('/Users/huangshaohua/Desktop/code/testcase/userservice')