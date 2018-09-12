import yaml

# 用于记录用户token和uid以及后续进行读取应用
fname = "../config/logininfo.yaml"


def GetToken(parem):
    pass


# 单独获取uid---主要提供sql中数据支持
def getUserId(parem, count=0):
  pass


def getUserLoginToken(parem):
    pass


def logininfotoYAML(apijson, usertype):
    token = apijson['model']['loginToken']
    uid = apijson['model']['userId']
    with open(fname, "r")as f:
        newinfo = yaml.load(f)
    if '新用户' in usertype:
        newinfo['newuser'] = {"uid": uid, "token": token}
        with open(fname, "w")as f:
            yaml.dump(newinfo, f)
        f.close()
