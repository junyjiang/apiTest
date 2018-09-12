# -*- coding: utf-8 -*-
import decimal
import json
import re

import pymysql
from jsonpath_rw import parse

from ForInterface.config.account import *
from .Logs import LOG

'''
返回json校验方法参数为：从Excel中读取的期望值data_test['qiwang']以及通过TestApi请求到的接口返回值
当前count参数是为了避免重复调用json.loads方法（因为此方法所要传递的参数是string类型不然会Error）
'''


def expectJson(asserqingwang, fanhuijson, count=0):
    result = False
    if count == 0:
        # 格式化期望结果为json对象
        asserqingwang = json.loads(asserqingwang)
        print('期望值：', asserqingwang, '\n', '实际返回值：', fanhuijson)
        # 校验返回数据是否有新的不包含在期望值中的key
        if checkParem(asserqingwang, fanhuijson):
            print('存在新字段:', checkParem(asserqingwang, fanhuijson))
    # 处理当调用时数据为默认通过的*号标识时不需要去校验格式的一致性（防止int型数据和str比较导致失败）
    if asserqingwang != '*':
        assert type(asserqingwang) == type(fanhuijson)
    # 若期望值为dict直接进行key的判断
    if isinstance(asserqingwang, dict):
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
        # for asserqi, fanhui in zip(sorted(asserqingwang), sorted(fanhuijson)):
        #     return (expectJson(asserqi, fanhui, count=1))
    # 返回数据给dict的处理逻辑或list处理逻辑最底层的判断方法，若key没有出错最终的校验结果由此产生
    elif asserqingwang == fanhuijson or asserqingwang == '*':
        return True
    else:
        print('数据校验失败：', '期望值字段：', str(asserqingwang), '实际返回字段：', str(fanhuijson))
        return False


# 检测接口是否有新增字段
def checkParem(qiwang, fanhui):
    newparem = []
    if type(qiwang) == str:
        qiwang = json.loads(qiwang)
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


# 校验数据库中数据与返回数据

def checkSqlData(apijson, jsonkey, sql, dbname='depository'):
    if jsonkey != None and sql != None and len(jsonkey) > 0 and len(sql) > 0:
        # 需要校验数据存在
        if len(jsonkey.split(',')) > 1:
            # LOG.info('需要校验的字段多于一个')
            # 需要校验的字段多于一个
            sql = sql.split('&')
            jsonkeydata = jsonkey.split(',')
            for i in range(len(jsonkeydata)):
                sqldata = mysqlassertdata('depository', sql[i])
                jsonpath_expr = parse("$.." + jsonkeydata[i])
                jsonno = [match.value for match in jsonpath_expr.find(apijson)]
                if len(jsonno[0]) > 1 and type(jsonno[0]) != dict:
                    for j in range(len(jsonno[0])):
                        value11 = []
                        value2 = sqldata[j]
                        value1 = jsonno[0][j]
                        for k in value1.keys():
                            if type(jsonno[0][k]) == float:
                                # if 'Amount' in k:
                                value1[k] = format(value1[k], ',')
                            value11.append(jsonno[0][j][k])
                        for j2 in range(len(value2)):
                            if (type(sqldata[j])) == decimal.Decimal:
                                sqldata[j] = format(sqldata[j], '.2f')
                            if value2[j2] in value11:
                                checkdata = True
                            else:
                                LOG.debug('数据库中值：' + str(value2) + '\n' + '错误字段：' + '\n',
                                          str(value2[j]) + '\n' + '服务器返回值：' + str(value11))
                                return False
                else:
                    # LOG.info('需要校验的字段是数据字典不需要进行遍历list')
                    if type(jsonno[0]) == dict:
                        # 需要校验的字段是数据字典不需要进行便利list
                        valued = []
                        for k in jsonno[0].keys():
                            if type(jsonno[0][k]) == float:
                                # if 'Amount' in k:
                                jsonno[0][k] = format(jsonno[0][k], ',')
                            valued.append(jsonno[0][k])
                        for j in range(len(sqldata)):
                            if (type(sqldata[j])) == decimal.Decimal:
                                sqldata[j] = format(sqldata[j], '.2f')
                            if sqldata[j] in valued:
                                checkdata = True
                            else:
                                print('数据库中值：', sqldata, '\n', '实际值：', str(valued), '\n', '错误字段：', str(sqldata[j]))
                                LOG.debug('数据库中值：' + str(sqldata), '实际值：' + str(valued) + '错误字段：' + str(sqldata[j]))
                                return False
                    else:
                        # 需要校验的数据是value
                        jsonpath_expr = parse("$.." + jsonkey)
                        jsonno = [match.value for match in jsonpath_expr.find(apijson)]
                        sqldata = mysqlassertdata(dbname='depository', strsql=sql[i])
                        if sqldata == jsonno:
                            checkdata = True
                        else:
                            print('数据库中值：', sqldata, '\n', '实际值：', jsonno)
                            LOG.debug('数据库中值：' + str(sqldata) + '实际值：' + str(jsonno))
                            return False
        else:
            # LOG.info('需要校验的字段只有一个')
            # 需要校验的字段只有一个
            if jsonkey == '*':
                jsonno = apijson
                jsonno[0] = jsonno
            else:
                jsonpath_expr = parse("$.." + jsonkey)
                jsonno = [match.value for match in jsonpath_expr.find(apijson)]
            sqldata = mysqlassertdata(dbname=dbname, strsql=sql)
            # 若数据库查询数据为空且接口返回的数据同样为空则直接通过
            # (re.compile('[a-zA-Z]|[0-9]|[\u4e00-\u9fa5]').findall(str(jsonno))--->正则查询jsonno中是否包含字母数字和中文若没查到则为False，not Flase==True
            if sqldata == '查询无数据' and not (re.compile('[a-zA-Z]|[0-9]|[\u4e00-\u9fa5]').findall(str(jsonno))):
                print('校验数据为空，数据库同样为空')
                return True
            elif sqldata != '查询无数据' and not re.compile('[a-zA-Z]|[0-9]|[\u4e00-\u9fa5]').findall(str(jsonno)):
                print('数据库查询数据', sqldata, '实际返回数据', jsonno)
                return False
            elif type(jsonno[0]) == dict:
                valued = []
                for k in jsonno[0].keys():
                    if type(jsonno[0][k]) == float:
                        jsonno[0][k] = format(jsonno[0][k], '.2f')
                    valued.append(jsonno[0][k])
                for j in range(len(sqldata)):
                    # 格式化浮点型数据
                    if (type(sqldata[j])) == decimal.Decimal:
                        sqldata[j] = format(sqldata[j], '.2f')
                    if sqldata[j] == '0.0':
                        sqldata[j] = '0'
                    # 读取数据库数据并确认返回值包含对应的数据
                    if sqldata[j] in valued:
                        checkdata = True
                    else:
                        print('数据库中值：', sqldata, '\n', '实际值：', jsonno, '错误字段：', sqldata[j], '第', j, '个字段', '\n', sql)
                        LOG.debug('数据库中值：' + str(sqldata) + '错误字段：' + str(sqldata[j]) + '第' + str(
                            j) + '个字段' + sql + '实际值：' + str(jsonno))
                        return False

            # 若返回数据长度为1且数据不是list直接比较数据库返回结果

            elif (len(jsonno) == 1 or len(jsonno[0] == 1)) and type(jsonno[0]) != list:
                if sqldata == jsonno:
                    checkdata = True
                else:
                    return False
            else:
                # 若数据为list进行
                for i in range(len(jsonno[0])):
                    value11 = []
                    value1 = jsonno[0][i]
                    for k in value1.keys():
                        if type(value1[k]) == float:
                            value1[k] = format(value1[k], '.2f')
                        value11.append(value1[k])
                    value2 = sqldata[i]
                    if type(value2) == list:
                        for j in range(len(value2)):
                            if (type(value2[j])) == decimal.Decimal:
                                value2[j] = format(value2[j], '.2f')
                            # if value2[j] == '0.00':
                            #     value2[j] = '0'
                            if value2[j] in value11:
                                checkdata = True
                            else:
                                print('数据库中值：', value2, '\n', '服务器返回值：', value11, '\n', '错误字段：', '\n', value2[j], '\n',
                                      sql)
                                LOG.debug('数据库中值：' + str(value2) + '\n' + '错误字段：' + '\n' + str(
                                    value2[j]) + '\n' + '服务器返回值：' + str(value11))
                                return False
                    else:
                        for j in range(len(sqldata)):
                            if (type(sqldata[j])) == decimal.Decimal:
                                sqldata[j] = format(sqldata[j], '.2f')
                            # if sqldata[j] == '0.00':
                            #     sqldata[j] = '0'
                            if sqldata[j] in value11:
                                checkdata = True
                            else:
                                print('数据库中值：', '\n', '服务器返回值：', value11, sqldata, '错误字段：', sqldata[j])
                                LOG.debug('数据库中值：' + str(sqldata) + '错误字段：' + str(sqldata[j]) + '\n',
                                          '服务器返回值：' + str(value11))
                                return False
        print('数据库中值：', sqldata, '\n', '服务器返回值：', jsonno)
        return checkdata
    elif jsonkey == None or sql == None:
        return True
    else:
        LOG.info('填写测试预期值')
        raise ('请输入要验证的字段')


# 获取查询出的数据个数==满足条件的数据行数
def mysqlassertnum(dbname, strsql):
    conn = pymysql.connect(host=Mysqlhost, port=3307, user=MysqlName, passwd=MysqlPassword, db=dbname, charset='utf8')
    cur = conn.cursor()
    cur.execute(strsql)
    curnum = cur.rowcount
    cur.close()
    conn.close()
    return curnum


# sql查询 查询结果（List）
def mysqlassertdata(dbname, strsql):
    conn = pymysql.connect(host=Mysqlhost, port=3307, user=MysqlName, passwd=MysqlPassword, db=dbname, charset='utf8')
    cur = conn.cursor()
    cur.execute(strsql)
    if (cur.rowcount > 0):
        data = cur.fetchall()
        sqldata = []
        if cur.rowcount > 1:
            for d in range(cur.rowcount):
                if len(data[d]) >= 1:
                    f = list(data[d])
                    sqldata.append(f)
        else:
            for d in range(cur.rowcount):
                if len(data[d]) > 1:
                    for i in range(len(data[d])):
                        f = data[d][i]
                        sqldata.append(f)
                else:
                    sqldata.append(data[d][0])
    else:
        sqldata = '查询无数据'
        print('没查到数据')
        LOG.info('没查到数据')
    cur.close()
    conn.close()
    return sqldata


# 操作数据库增、删数据
def editData(dbname, strsql):
    conn = pymysql.connect(host=Mysqlhost, port=3307, user=MysqlName, passwd=MysqlPassword, db=dbname, charset='utf8')
    cur = conn.cursor()
    sta = cur.execute(strsql)
    if sta == 1:
        conn.commit()
    else:
        LOG.info('编辑失败', strsql)
    cur.close()
    conn.close()
