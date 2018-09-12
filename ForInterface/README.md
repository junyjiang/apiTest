# 接口测试框架（python3,不兼容python2.x版本） 
## 注：现在基于Excel文件管理测试用例基本实现
### 使用的库 requests，绝大部分是基于Python原有的库进行的，这样简单方便，
### 使用脚本参数，尽可能降低代码的耦合度。
#目录结构
### 1.config文件yaml管理发送邮件配置，account提供账号支持
### 2.Interface对测试接口相关的封装，包括requests库
### 3.log文件夹用来存放日志日志日志，
### 4.Public 展示测试报告相关以及一些公共方法
### 5.test_Case文件夹用来存放我们的测试用例相关的，
### 6.test_Data用来存储我们的测试数据，Excel管理测试用例
### 7.test_report 存放测试报告，
### 8.newruuner.py 主运行文件。
### 9.重写了BSTestRunner中的部分实现，
更改：显示中文测试用例名称；更改失败用例输出只输出需要打印的日志，不输出assert方法的原始输出
增加：增加了skiptestcase显示1
当前框架借鉴前人轮子：
https://github.com/liwanlei/jiekou-python3
by@liwanlei



