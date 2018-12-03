# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/11/7 0007
__author__ = 'huohuo'
import os
import requests
import logging
import time
import socket
import zipfile
import re
from JYAliYun.AliYunMNS.AliMNSServer import MNSServerManager

# "错误消息通知群"
# "霍佩佩专用机器人"
# "e61184c4450f33a3313dc5651f7e63ed64c1e2e1f4dd37b585ffda93e9e801ee",
# 前端测试 通知
# https://oapi.dingtalk.com/robot/send?access_token=f0e012537fb60ac5e37be4239e9380e574eb65574f36446f7160750db9f413fe
#! /usr/bin/env python
# coding: utf-8


def test_chinese(contents):
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    # 一个小应用，判断一段文本中是否包含简体中：
    match = zhPattern.search(contents)
    if match:
        a = zhPattern.findall(contents)
        ch_num = 0
        for i in a:
            ch_num += len(i)
        return ch_num
    return 0


def sex2str(sex):
    if sex == 0:
        return '未知'
    elif sex == 1:
        return '男'
    else:
        return '女'


def float2percent(p):
    f = str(p).strip()
    if f in [u'无', 'None', '']:
        return 'N/A'
    elif f == "<1%":
        return f.replace("<", "&lt;")
    elif f == ">99%":
        return f
    elif '%' in f:
        return f
    else:
        f = '%.2f%%' % float(f)
    return f


def int2ch(i):
    chs = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    return chs[i]


def zip_dir(lodurl, dirname, zipfilename):
    filelist = []
    #Check input ...
    fulldirname = dirname
    fullzipfilename = lodurl + zipfilename
    print "Start to zip %s to %s ..." % (fulldirname, fullzipfilename)
    if not os.path.exists(fulldirname):
        print "Dir/File %s is not exist, Press any key to quit..." % fulldirname
        inputStr = raw_input()
        return
    if os.path.isdir(fullzipfilename):
        tmpbasename = os.path.basename(dirname)
        fullzipfilename = os.path.normpath(os.path.join(fullzipfilename, tmpbasename))
    if os.path.exists(fullzipfilename):
        print "%s has already exist, are you sure to modify it ? [Y/N]" % fullzipfilename
        while 1:
            inputStr = raw_input()
            if inputStr == "N" or inputStr == "n" :
                return
            else:
                if inputStr == "Y" or inputStr == "y" :
                    print "Continue to zip files..."
                    break

    #Get file(s) to zip ...
    if os.path.isfile(dirname):
        filelist.append(dirname)
        dirname = os.path.dirname(dirname)
    else:
        #get all file in directory
        for root, dirlist, files in os.walk(dirname):
            for filename in files:
                filelist.append(os.path.join(root,filename))

    #Start to zip file ...
    destZip = zipfile.ZipFile(fullzipfilename, "w")
    i = 0
    for eachfile in filelist:
        destfile = eachfile[len(dirname):]
        print "Zip file %s..." % destfile
        destZip.write(eachfile, destfile)
        i += 1
    destZip.close()
    if i == len(filelist):
        return 5
    else:
        return 3


def roman_to_int(s):
    #     1~10: I II III IV V VI VII VIII IX X
    #     11~20: XI XII XIII XIV XV XVI XVII XVIII XIX XX
    """
    :type s: str
    :rtype: int
    """

    if s == 'Ⅲ':
        return 3
    elif s == 'Ⅴ':
        return 5
    elif s == 'Ⅷ':
        return 8
    else:
        try:
            romanInt = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100,'D': 500,'M': 1000}
            num = romanInt[s[0]]
            for i in range(1,len(s)):
                if romanInt[s[i]] > romanInt[s[i - 1]]:
                    num += romanInt[s[i]] - 2 * romanInt[s[i - 1]]
                else:
                    num += romanInt[s[i]]
            return num
        except:
            try:
                return int(s)
            except:
                print s


def send_msg_by_dd(message, **kwargs):
    """
    消息类型为文本时，data 格式如下：
    data = {
        "msgtype": "text",
        "text": {
            "content": "错误日志通知测试2017-08-21 10:14"
        },
        "at": {
            "atMobiles": [
                "18612660303",
                "15538819853"
            ],
            "isAtAll": True # True 表示@ALL, False 表示只 @ atMobiles 中的
        }
    }
    :param message:
    :param type: 消息类型，默认 text
    :param kwargs: 备用参数: mobile_phone 手机号，表示通知人，
                            access_token 通知机器人值，表示用哪个机器人
    :return:
    """
    use_mns = False
    MNS_CONF_PATH = ''
    message += '【时间】：%s' % format_time()
    if 'MNS_CONF_PATH' in os.environ:
        MNS_CONF_PATH = os.environ['MNS_CONF_PATH']
        if os.path.exists(MNS_CONF_PATH):
            use_mns = True
        else:
            message = '\n【MNS_CONF_FILE】： %s not exists.\n\n%s\n' % (MNS_CONF_PATH, message)

    if use_mns:
        mns_server = MNSServerManager(conf_path=MNS_CONF_PATH)
        mns_topic = mns_server.get_topic("JYWaring")
        mns_topic.publish_message(message, "前端错误", is_thread=False)
    else:
        access_token = "e61184c4450f33a3313dc5651f7e63ed64c1e2e1f4dd37b585ffda93e9e801ee"
        env = get_value(kwargs, 'env', '环境')
        if env.startswith('Development'):
            access_token = 'f0e012537fb60ac5e37be4239e9380e574eb65574f36446f7160750db9f413fe'
        mobile_phone = "15538819853" if "mobile_phone" not in kwargs else kwargs['mobile_phone']
        txt_data = {
            "msgtype": "text",
            "text": {"content": '【Env】: %s\n%s' % (env, message)},
            "at": {"atMobiles": [mobile_phone], "isAtAll": False}
        }
        url = "https://oapi.dingtalk.com/robot/send?access_token=%s" % access_token
        header = {"Content-Type": "application/json"}
        try:
            requests.post(url, json=txt_data, headers=header, timeout=2)
        except Exception, e:
            logging.error(e.args)


def format_time(t=None, frm="%Y-%m-%d %H:%M:%S"):
    if t is None:
        t = time.localtime()
    if type(t) == int:
        t = time.localtime(t)
    my_time = time.strftime(frm, t)
    return my_time


def get_host(web_port, print_msg=''):
    host_name = socket.gethostname()
    host = socket.gethostbyname(host_name)
    url = ':'.join([host, web_port])
    print 'ip: "%s", name: %s, port: %d' % (host, host_name, web_port)
    print url
    if len(print_msg) > 0:
        print print_msg
    return {'ip': host, 'name': host_name, 'port': web_port, 'url': url}


def get_value(disease_item, key, null=None):
    if isinstance(disease_item, dict):
        if key in disease_item:
            value = disease_item[key]
            if value is None:
                return null
            if isinstance(value, unicode) or isinstance(value, str):
                if value.strip() == '':
                    return null
                return value.strip()
            return value
    return null


if __name__ == "__main__":
    pass
    

