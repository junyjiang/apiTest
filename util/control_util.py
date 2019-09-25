# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 9:51
# @Author  : jiangchao
import os
import time
import yaml

basepath = os.path.dirname(os.path.dirname(__file__))


def choiceserver(servicename):
    with open(basepath+'/config/hostmanage.yaml', "r") as f1:
        hostinfo = yaml.load(f1)
        host = hostinfo[servicename]
        return host
def importparam(argv):
    service = []
    serverlist = argv[0].split(',')
    for sername in serverlist:
        if sername != ',':
            service.append(sername)
        else:
            pass
    branchlist =argv[1].split(',')
    branch = []
    for braname in branchlist:
        if braname != ',':
            branch.append(braname)
        else:
            pass
    return service,branch

def choicedb(path):
    try:
        with open(path,"r",encoding='utf-8') as db:
            db = yaml.load(db)
            dbinfo=[db['dbhost'],db['dbport'],db['dbusername'],db['dbpassword'],db['dbname'],db['servername'],db['serverpassword'],db['serverport']]
        return dbinfo
    except Exception as e:
        print(path, e)
def gettime():
    return str(time.time()).replace('.', '0')
def formatparam(data):
    start = []
    end = []
    s = 0
    if len(data)>4 and data[0] == '{' and data[-1] =='}':
        data =data.replace("'",'"')
    else:
        while data.find('{', s, int(len(data))) != -1:
            start.append(data.find('{', s, int(len(data))))
            end.append(data.find('}', s, int(len(data))))
            s = data.find('}', s, int(len(data))) + 1
        for (s, e) in zip(start, end):
            jsonstr = (data[s:e + 1]).replace("'", '"')
            data = data.replace(data[s:e + 1], jsonstr)
    return data
# print(formatparam("{'class':'com.tritonsfs.cac.depository.entity.vo.ucs.UserVO','model':{'availableAmount':null,'bankcardNo':null,'coinNum':null,'device':null,'email':null,'emailBindTime':null,'emailCheck':null,'flow':null,'growthNum':null,'guaranteeCode':null,'guarateeName':null,'highestLevel':null,'id':null,'idCardNo':null,'idCardType':null,'inviteCode':null,'isAdvance':null,'isAgree':null,'isNew':null,'isOffline':null,'isOpenAccount':null,'isPassRiskRating':null,'isStock':null,'level':null,'mobile':null,'myInviteCode':null,'openBeginTime':'2019:01:28','openEndTime':'2019:04:28','openTime':null,'pageNum':1,'pageSize':10,'phoneNo':null,'realName':null,'regBeginTime':'2019:01:01','regEndTime':'2019:04:28','regPlatform':null,'regSource':null,'regTime':null,'sex':null,'status':null,'stockStatus':null,'tokenValideTime':null,'type':null,'userRole':null,'userType':null},'order':[],'pageNum':1,'pageSize':10},'1312',{'jaon':'tkslj'}'"))
