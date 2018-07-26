import time
# 公共方法实现
# 通过接口获取新手标的编号

# 判断计划第一个标的是否为新手标

#  通过接口获取标的编号===loanid
#  获取产品列表中的标的的id用来投资等
# 单独获取带有还款计划的标的ID
# 债转标的还款计划是初始标的的还款计划，通过此获取到债转标的对应的原始标的ID

# 获取用户投资记录中的标的信息
# 获取是否含有投资记录-->最终判断方式是可投金额是否小于招标金额
# 获取标的最小可投金额
# 获取剩余可投金额
# 获取投资梯度
#简单封装replace方法，将异常处理放在公共方法中
def replaceData(data,restr,newstr):
    if data != None:
        newstr = data.replace(restr,str(newstr))
    else:
        newstr = None
    return newstr
#获取红包id
#获取加息券id


#获取交易系统orderid
# 获取解冻批次号


# 获取银行orderid

#获取交易状态

#获取账户金额


def gettime():
    return str(time.time()).replace('.', '0')

# 获取需要操作的账号信息






