import time


# 公共方法实现
# 简单封装replace方法，将异常处理放在公共方法中
def replaceData(data, restr, newstr):
    if data != None:
        newstr = data.replace(restr, str(newstr))
    else:
        newstr = None
    return newstr


def gettime():
    return str(time.time()).replace('.', '0')
