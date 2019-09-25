# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 9:51
# @Author  : jiangchao
import os
import re
import json
from util.control_util import choicedb
from util.db_connect import mysqlassertdata


'''校验Response中是否存在新字段'''
def checkParem(qiwang, fanhui):

    if type(qiwang) == dict:
        try:
            newparem = []
            if type(qiwang) == str:
                qiwang = json.loads(qiwang)
            if type(fanhui) == str:
                fanhui = json.loads(fanhui)
            for k in list(fanhui.keys()):
                if len(list(fanhui.keys())) != len(list(qiwang.keys())):
                    for j in list(fanhui.keys()):
                        if j not in list(qiwang.keys()):
                            newparem.append(j)
                    return newparem
                if k not in qiwang.keys():
                    return newparem
                elif type(fanhui[k]) == dict and qiwang[k] != "*":
                    return checkParem(qiwang[k], fanhui[k])
        except Exception as e:
            print('检查是否有新参数出现出错', e)
    else:
        return False


'''
返回json校验方法参数为：从csv中读取的期望值data_test['qiwang']以及通过TestApi请求到的接口返回值
当前count参数是为了避免重复调用json.loads方法（因为此方法所要传递的参数是string类型不然会Error）
'''


def expectJson(asserqingwang, fanhuijson, count=0):
    if asserqingwang == 'True':
        asserqingwang = True
    elif asserqingwang =='False':
        asserqingwang=False
    else:
        pass
    result = False
    if count == 0 and type(asserqingwang) != bool:
        # 为了减少异常返回时测试报告的输出清晰在含有异常时不在直接输出期望和实际值
        # 仍会在校验失败后输出对应值
        if 'Exception' not in str(fanhuijson):
            print('期望值：', str(asserqingwang) + '\n' + '实际值：', str(fanhuijson))
        else:
            pass
        # 格式化期望结果为json对象
        asserqingwang = asserqingwang.replace(': False',": 'False'")
        asserqingwang = asserqingwang.replace(': True', ": 'True'")
        asserqingwang =asserqingwang.replace("'",'"')
        try:
            asserqingwang = json.loads(asserqingwang)
        except Exception as e:
            print(e)
        # 校验返回数据是否有新的不包含在期望值中的key
    if checkParem(asserqingwang, fanhuijson):
        print('存在新字段:', checkParem(asserqingwang, fanhuijson))
        return False
    # 处理当调用时数据为默认通过的*号标识时不需要去校验格式的一致性（防止int型数据和str比较导致失败）
    if asserqingwang != '*' and type(asserqingwang) == type(fanhuijson):
        pass
    elif asserqingwang != '*' and type(asserqingwang) != type(json.loads(str(fanhuijson))):
        print('校验字段类型错误:', '\n' ,'期望值：', asserqingwang, '\n', '实际值：', fanhuijson, '\n', type(asserqingwang), type(fanhuijson))
        return False
    # 若期望值为dict直接进行key的判断
    if isinstance(asserqingwang, dict):
        if type(fanhuijson) == str:
            fanhuijson = json.loads(fanhuijson)
        for key in asserqingwang:
            # 判断fanhuijson中是否包含了期望值的key
            if fanhuijson.__contains__(key):
                # 递归调用当前方法校验期望KEY对应的value
                result = expectJson(asserqingwang[key], fanhuijson[key], count=1)
                if not result:
                    print('失败数据对应Key：', key, '<----')
                    break
            else:
                print('数据校验失败：', '异常字段：', str(key))
                return False
        # 由于最初的调用是dict所以校验方法最后出口是这里
        return result
    # 若期望结果是list则进入此方法进行校验
    elif isinstance(asserqingwang, list) and len(asserqingwang) >= 1:
        for i in range(len(asserqingwang)):
            # 将list中的元素递归校验->可能直接走入字符串判断逻辑也可能走入dict判断逻辑，当前的return的数据不是直接给到case层而是回掉给dict层判断逻辑
            result = expectJson(asserqingwang[i], fanhuijson[i], count=1)
            if not result:
                break
        return result
    # 返回数据给dict的处理逻辑或list处理逻辑最底层的判断方法，若key没有出错最终的校验结果由此产生
    elif asserqingwang == fanhuijson or asserqingwang == '*':
        return True
    else:
        print('数据校验失败：', '期望值字段：', str(asserqingwang)+'\n'+'实际返回字段：', str(fanhuijson))
        return False



# new 数据库校验
def checkSqlData(curpath,assertdata, sql):
    sql = sql[0]
    # sourcepath = os.getcwd()
    dbinfopath = curpath +'/conf/db_info.yaml'
    print(curpath +'/conf/db_info.yaml')
    dbinfo = choicedb(dbinfopath)
    # 存在需要校验数据
    if assertdata != "*" and sql != "*" and len(str(assertdata))> 0 and len(sql) > 2:
        ## 需要校验的字段多于一个
        if len(assertdata.split('|||')) > 1:
            #切割sql
            sql = sql.split('|||')
            #切割校验字段
            assertdata = assertdata.split('|||')
            for i in range(len(assertdata)):
                mysqldata=mysqlassertdata(dbinfo, sql[i])
                datalist = assertdata[i].split(',')
                if isinstance(datalist, list):
                    for (value,sqldata) in zip(datalist,mysqldata):
                        if value == sqldata or value == str(sqldata) or str(value) == sqldata:
                            checkresult = True
                        else:
                            print('数据库中值：', sqldata, '\n', '期望值：', value, '错误sql：', '\n', sql[i], '第', mysqldata[i].index(sqldata), '个字段')
                            return False
                #根据sql语句查询数据后进行比较
                elif assertdata[i] == mysqlassertdata(dbinfo, sql[i]):
                    checkresult = True
                else:
                     return False
            return checkresult
        else:
            # 需要校验的字段只有一个
            print('**',sql)
            mysqldata = mysqlassertdata(dbinfo, sql)
            assertdata = assertdata.split(',')
            if isinstance(assertdata, list):
                for (value,sqldata) in zip(assertdata,mysqldata):
                    if value == sqldata or value==str(sqldata):
                        checkresult = True
                    else:
                        print('数据库中值：', sqldata, '\n', '期望值：', value, '\n', '错误sql：', sql,'\n', '第', mysqldata.index(sqldata), '个字段')
                        return False
                return checkresult
            #根据sql语句查询数据后进行比较
            if assertdata == mysqldata or assertdata == str(mysqldata) or str(assertdata) == mysqldata:
                checkresult = True
            else:
                print('数据库中值：', mysqldata, '\n', '期望值：', assertdata,'\n', '错误sql：',  sql)
                return False
            return checkresult
    else:
        return True

# 废弃
# 校验数据库中数据与返回数据
# def checkSqlData(apijson, jsonkey, sql):
#     sourcepath = os.getcwd()
#     dbinfopath = sourcepath +'/conf/db_info.yaml'
#     dbinfo = choicedb(dbinfopath)
#     if jsonkey != "*" and sql != "*" and len(jsonkey) > 0 and len(sql) > 0:
#         # 需要校验数据存在
#         if len(jsonkey.split(',')) > 1:
#             # LOG.info('需要校验的字段多于一个')
#             # 需要校验的字段多于一个
#             sql = sql.split('&')
#             jsonkeydata = jsonkey.split(',')
#             for i in range(len(jsonkeydata)):
#                 sqldata = mysqlassertdata(dbinfo, sql[i])
#                 jsonpath_expr = parse("$.." + jsonkeydata[i])
#                 jsonno = [match.value for match in jsonpath_expr.find(apijson)]
#                 if len(jsonno[0]) > 1 and type(jsonno[0]) != dict:
#                     for j in range(len(jsonno[0])):
#                         value11 = []
#                         value2 = sqldata[j]
#                         value1 = jsonno[0][j]
#                         for k in value1.keys():
#                             if type(jsonno[0][k]) == float:
#                                 # if 'Amount' in k:
#                                 value1[k] = format(value1[k], ',')
#                             value11.append(jsonno[0][j][k])
#                         for j2 in range(len(value2)):
#                             if (type(sqldata[j])) == decimal.Decimal:
#                                 sqldata[j] = format(sqldata[j], '.2f')
#                             if value2[j2] in value11:
#                                 checkdata = True
#                             else:
#                                 LOG.debug('数据库中值：' + str(value2) + '\n' + '错误字段：' + '\n',
#                                           str(value2[j]) + '\n' + '服务器返回值：' + str(value11))
#                                 return False
#                 else:
#                     # LOG.info('需要校验的字段是数据字典不需要进行遍历list')
#                     if type(jsonno[0]) == dict:
#                         # 需要校验的字段是数据字典不需要进行便利list
#                         valued = []
#                         for k in jsonno[0].keys():
#                             if type(jsonno[0][k]) == float:
#                                 # if 'Amount' in k:
#                                 jsonno[0][k] = format(jsonno[0][k], ',')
#                             valued.append(jsonno[0][k])
#                         for j in range(len(sqldata)):
#                             if (type(sqldata[j])) == decimal.Decimal:
#                                 sqldata[j] = format(sqldata[j], '.2f')
#                             if sqldata[j] in valued:
#                                 checkdata = True
#                             else:
#                                 print('数据库中值：', sqldata, '\n', '实际值：',
#                                       str(valued), '\n', '错误字段：', str(sqldata[j]))
#                                 LOG.debug('数据库中值：' + str(sqldata), '实际值：' +
#                                           str(valued) + '错误字段：' + str(sqldata[j]))
#                                 return False
#                     else:
#                         # 需要校验的数据是value
#                         jsonpath_expr = parse("$.." + jsonkey)
#                         jsonno = [match.value for match in jsonpath_expr.find(apijson)]
#                         sqldata = mysqlassertdata(dbname='depository', strsql=sql[i])
#                         if sqldata == jsonno:
#                             checkdata = True
#                         else:
#                             print('数据库中值：', sqldata, '\n', '实际值：', jsonno)
#                             LOG.debug('数据库中值：' + str(sqldata) + '实际值：' + str(jsonno))
#                             return False
#         else:
#             # LOG.info('需要校验的字段只有一个')
#             # 需要校验的字段只有一个
#             if jsonkey == '*':
#                 jsonno = apijson
#                 jsonno[0] = jsonno
#             else:
#                 jsonpath_expr = parse("$.." + jsonkey)
#                 jsonno = [match.value for match in jsonpath_expr.find(apijson)]
#             sqldata = mysqlassertdata(dbinfo, sql)
#             # 若数据库查询数据为空且接口返回的数据同样为空则直接通过
#             # (re.compile('[a-zA-Z]|[0-9]|[\u4e00-\u9fa5]').findall(str(jsonno))--->正则查询jsonno中是否包含字母数字和中文若没查到则为False，not Flase==True
#             if sqldata == '查询无数据' and not ((re.compile('[a-zA-Z]|[0-9]|[\u4e00-\u9fa5]').findall(str(jsonno))) and jsonno[0] != None):
#                 print('校验数据为空，数据库同样为空')
#                 return True
#             elif sqldata != '查询无数据' and not re.compile('[a-zA-Z]|[0-9]|[\u4e00-\u9fa5]').findall(str(jsonno)):
#                 print('数据库查询数据', sqldata, '实际返回数据', jsonno)
#                 return False
#             elif type(jsonno[0]) == dict:
#                 valued = []
#                 for k in jsonno[0].keys():
#                     if type(jsonno[0][k]) == float:
#                         jsonno[0][k] = format(jsonno[0][k], '.2f')
#                     valued.append(jsonno[0][k])
#                 for j in range(len(sqldata)):
#                     # 格式化浮点型数据
#                     if (type(sqldata[j])) == decimal.Decimal:
#                         sqldata[j] = format(sqldata[j], '.2f')
#                     if sqldata[j] == '0.0':
#                         sqldata[j] = '0'
#                     # 读取数据库数据并确认返回值包含对应的数据
#                     if sqldata[j] in valued:
#                         checkdata = True
#                     else:
#                         print('数据库中值：', sqldata, '\n', '实际值：', jsonno, '错误字段：', sqldata[j], '第', j, '个字段', '\n', sql)
#                         LOG.debug('数据库中值：' + str(sqldata) + '错误字段：' + str(sqldata[j]) + '第' + str(
#                             j) + '个字段' + sql + '实际值：' + str(jsonno))
#                         return False
#
#             # 若返回数据长度为1且数据不是list直接比较数据库返回结果
#
#             elif (len(jsonno) == 1 or len(jsonno[0] == 1)) and type(jsonno[0]) != list:
#                 if sqldata == jsonno:
#                     checkdata = True
#                 else:
#                     return False
#             else:
#                 # 若数据为list进行
#                 for i in range(len(jsonno[0])):
#                     value11 = []
#                     value1 = jsonno[0][i]
#                     for k in value1.keys():
#                         if type(value1[k]) == float:
#                             value1[k] = format(value1[k], '.2f')
#                         value11.append(value1[k])
#                     value2 = sqldata[i]
#                     if type(value2) == list:
#                         for j in range(len(value2)):
#                             if (type(value2[j])) == decimal.Decimal:
#                                 value2[j] = format(value2[j], '.2f')
#                             # if value2[j] == '0.00':
#                             #     value2[j] = '0'
#                             if value2[j] in value11:
#                                 checkdata = True
#                             else:
#                                 print('数据库中值：', value2, '\n', '服务器返回值：', value11, '\n', '错误字段：', '\n', value2[j], '\n',
#                                       sql)
#                                 LOG.debug('数据库中值：' + str(value2) + '\n' + '错误字段：' + '\n' + str(
#                                     value2[j]) + '\n' + '服务器返回值：' + str(value11))
#                                 return False
#                     else:
#                         for j in range(len(sqldata)):
#                             if (type(sqldata[j])) == decimal.Decimal:
#                                 sqldata[j] = format(sqldata[j], '.2f')
#                             # if sqldata[j] == '0.00':
#                             #     sqldata[j] = '0'
#                             if sqldata[j] in value11:
#                                 checkdata = True
#                             else:
#                                 print('数据库中值：', '\n', '服务器返回值：', value11, sqldata, '错误字段：', sqldata[j])
#                                 LOG.debug('数据库中值：' + str(sqldata) + '错误字段：' + str(sqldata[j]) + '\n',
#                                           '服务器返回值：' + str(value11))
#                                 return False
#         print('数据库中值：', sqldata, '\n', '服务器返回值：', jsonno)
#         return checkdata
#     # elif jsonkey == None or sql == None:
#     #     return True
#     else:
#         return True
#         # LOG.info('填写测试预期值')
#         # raise ('请输入要验证的字段')





