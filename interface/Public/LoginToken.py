import yaml

# 用于记录用户token和uid以及后续进行读取应用
fname = "../config/logininfo.yaml"


def GetToken(parem):
    if parem == None:
        return parem
    with open(fname, "r")as f:
        newinfo = yaml.load(f)
    if 'transaction' in parem:
        uid = newinfo['transactionuser']['uid']
        token = newinfo['transactionuser']['token']
        parem = parem.replace('transactionuid', 'uid')
        parem = parem.replace('transactionlogintoken', 'logintoken')
    elif 'old' in parem:
        uid = newinfo['olduser']['uid']
        token = newinfo['olduser']['token']
        parem = parem.replace('olduid', 'uid')
        parem = parem.replace('oldlogintoken', 'logintoken')
    else:
        uid = newinfo['newuser']['uid']
        token = newinfo['newuser']['token']
    f.close()
    # 直接替换请求参数中的uid和logintoken
    if 'uid' in parem and 'logintoken' not in parem:
        parem = parem.replace('uid', uid)
        return parem
    elif 'logintoken' in parem and 'uid' not in parem:
        parem = parem.replace('logintoken', token)
        return parem
    elif 'uid' in parem and 'logintoken' in parem:
        parem = parem.replace('uid', uid)
        parem = parem.replace('logintoken', token)
        return parem
    else:
        return parem


# 单独获取uid---主要提供sql中数据支持
def getUserId(parem, count=0):
    if parem == None:
        return 'uid'
    uid = '登录失败'
    with open(fname, "r")as f:
        newinfo = yaml.load(f)
    if 'transaction' in parem:
        uid = newinfo['transactionuser']['uid']
    elif 'old' in parem:
        uid = newinfo['olduser']['uid']
    else:
        uid = newinfo['newuser']['uid']
    f.close()
    return uid


def getUserLoginToken(parem):
    if parem == None:
        return 'loginToken'
    with open(fname, "r")as f:
        newinfo = yaml.load(f)
    if 'old' in parem:
        loginToken = newinfo['olduser']['token']
    elif 'transaction' in parem:
        loginToken = newinfo['transactionuser']['token']
    else:
        loginToken = newinfo['newuser']['token']
    f.close()
    return loginToken


def logininfotoYAML(apijson, usertype):
    token = apijson['model']['loginToken']
    uid = apijson['model']['userId']
    with open(fname, "r")as f:
        newinfo = yaml.load(f)
    if '新用户' in usertype:
        newinfo['newuser'] = {"uid": uid, "token": token}
        with open(fname, "w")as f:
            yaml.dump(newinfo, f)
    elif '老用户' in usertype:
        newinfo['olduser'] = {"uid": uid, "token": token}
        with open(fname, "w")as f:
            yaml.dump(newinfo, f)
    elif '交易' in usertype:
        newinfo['transactionuser'] = {"uid": uid, "token": token}
        with open(fname, "w")as f:
            yaml.dump(newinfo, f)
        f.close()
