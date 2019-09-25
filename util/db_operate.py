# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 9:51
# @Author  : jiangchao
import os
import sys
import zipfile
from paramiko import SFTPClient, SSHClient, AutoAddPolicy
from paramiko.transport import Transport
from util.control_util import choicedb
from util.db_connect import mysqlassertdata, editData
if sys.platform != 'win32':
    from pexpect import spawn


def deletedata(path):
    dbinfo = choicedb(path+'/conf/db_info.yaml')
    s = sshconnect(hostname=dbinfo[0], port=dbinfo[7], username=dbinfo[5], password=dbinfo[6])
    s.exec_command('rm -rf /home/mysql/basedata/initdata.sql')
    s.exec_command('rm -rf /home/mysql/backup/databackup.sql')
    if sys.platform == 'win32':
        path = path.replace('/','\\')
        os.popen('del '+path+'\\database\\backupdatabase.zip')
        print('del '+path+'\\database\\backupdatabase.zip')
        os.popen('del '+path+'\\database\\databackup.sql')
        print('del '+path+'\\database\\databackup.sql')
    else:
        os.popen('rm -rf '+path+'/database/databackup.sql')
        os.popen('rm -rf '+path+'/database/backupdatabase.zip')
    strsql = "select concat('delete from ',table_name,';') from information_schema.TABLES where table_schema=" +"'"+dbinfo[4] +"'"+";"
    droplist = mysqlassertdata(dbinfo,strsql)
    editData(dbinfo, droplist)
    return mysqlassertdata(dbinfo,strsql)



def dbbackup(path):
    dbinfo = choicedb(path + '/conf/db_info.yaml')
    s = sshconnect(hostname=dbinfo[0], port=dbinfo[7], username=dbinfo[5], password=dbinfo[6])
    st, std, stde = s.exec_command('cd /home/mysql/backup'+'\n' 'ls')
    filelist = std.read().decode('gbk',errors='ignore').split('\n')
    if 'databackup.sql' in filelist:
        s.exec_command('cd /home/mysql/backup'+'\n' 'rm -rf databackup1.sql')
    stdin, stdout, stderr = s.exec_command('mysqldump -t -u'+dbinfo[2]+' -p'+dbinfo[3]+' '+dbinfo[4]+' >/home/mysql/backup/databackup.sql')
    if 'error' not in stderr.read().decode('gbk', errors='ignore'):
        t1,t2,t3=s.exec_command('du -b /home/mysql/databackup.sql')
        if sys.platform == 'win32':
            t = Transport(dbinfo[0], 22)
            t.connect(username=dbinfo[5], password=dbinfo[6])
            sftp = SFTPClient.from_transport(t)
            src = '/home/mysql/backup/databackup.sql'
            des = path + '/database/databackup.sql'
            sftp.get(src, des)
            t.close()
        else:
            child = spawn(
                'scp ' + dbinfo[5] + '@' + dbinfo[0] + ':/home/mysql/backup/databackup.sql ' + path + '/database/')
            child.expect("password:")
            child.sendline(dbinfo[6])
            child.read()
        with zipfile.ZipFile(path + '/database/backupdatabase.zip', 'w') as z:
            z.write(path + '/database/databackup.sql')
        return t2.read().decode('gbk',errors='ignore').split('\t')[0].strip()
    else:
        return False
    s.close


def restore(path):

    dbinfo = choicedb(path+'/conf/db_info.yaml')
    editData(dbinfo, [['reset master;']])
    if sys.platform == 'win32':
        t = Transport(dbinfo[0], 22)
        t.connect(username=dbinfo[5], password=dbinfo[6])
        sftp = SFTPClient.from_transport(t)
        src = '/home/mysql/basedata/initdata.sql'
        des = path + '/database/initdata.sql'
        sftp.put(des,src )
        t.close()
    else:
        child = spawn(
            'scp '+path+'/database/initdata.sql '+ dbinfo[5]+'@'+dbinfo[0]+':/home/mysql/basedata/')
        child.expect("password:")
        child.sendline(dbinfo[6])
        child.read()
        child.close()
    s = sshconnect(hostname=dbinfo[0], port=dbinfo[7], username=dbinfo[5], password=dbinfo[6])
    st, std, stde = s.exec_command('cd /home/mysql/basedata' + '\n' 'ls')
    filelist = std.read().decode('gbk', errors='ignore').split('\n')
    if 'initdata.sql' in filelist:
        stdin, stdout, stderr=s.exec_command('mysql -u'+dbinfo[2]+' -p'+"'"+dbinfo[3]+"'"' '+dbinfo[4]+' </home/mysql/basedata/initdata.sql')
    return stderr.read().decode('gbk', errors='ignore')



def sshconnect(hostname,username,password,port):
    s = SSHClient()
    s.set_missing_host_key_policy(AutoAddPolicy())
    s.connect(hostname=hostname, port=port, username=username, password=password)
    return s

if __name__ == '__main__':
    pass
    # deletedata('D:/cac-servicestest/testcase/friendservice')
    # time.sleep(3)
    # restore('D:\cac-servicestest/testcase/friendservice')
    # time.sleep(3)
    # dbbackup('/Users/huangshaohua/Desktop/cac-servicestest/testcase/friendservice')
    # time.sleep(3)

    # restore()
    # dbbackup()