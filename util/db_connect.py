# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 9:51
# @Author  : jiangchao
import time

import pymysql

from util.Log import LOG


#连接db
def mysqlconnect(dbinfo):
    conn = pymysql.connect(host=dbinfo[0], port=int(dbinfo[1]), user=dbinfo[2], passwd=dbinfo[3], db=dbinfo[4], charset='utf8')
    return conn

# 获取查询出的数据个数==满足条件的数据行数
def mysqlassertnum(dbname, strsql):
    conn = mysqlconnect()
    # conn = pymysql.connect(host=Mysqlhost, port=dbporn, user=MysqlName, passwd=MysqlPassword, db=dbname, charset='utf8')
    cur = conn.cursor()
    cur.execute(strsql)
    curnum = cur.rowcount
    cur.close()
    conn.close()
    return curnum


# sql查询 查询结果（List）
def mysqlassertdata(dbinfo, strsql):
    conn = pymysql.connect(host=dbinfo[0], port=int(dbinfo[1]), user=dbinfo[2], passwd=dbinfo[3], db=dbinfo[4], charset='utf8')
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
def editData(dbinfo,strsql):
    conn = pymysql.connect(host=dbinfo[0], port=int(dbinfo[1]), user=dbinfo[2], passwd=dbinfo[3], db=dbinfo[4], charset='utf8')
    # conn = pymysql.connect(host=Mysqlhost, port=3307, user=MysqlName, passwd=MysqlPassword, db=dbname, charset='utf8')
    cur = conn.cursor()
    for sql in strsql:
        try:
            sta = cur.execute(sql[0])
            conn.commit()
        except Exception as e:
            print(e,sql[0])
    cur.close()
    conn.close()



if __name__ == '__main__':
    dbinfo = ['172.16.21.151', '3307', 'pc', '1q2t3q', 'depository']
    print(mysqlassertdata(dbinfo, 'select friends_num from friends_user where user_id = 105462271514;'))
