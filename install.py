#@author : Wangs_official
import os.path
import subprocess
import sys
import pip
import pip._internal
import logging
import getpass
import time
import json
print('[~]Author:Wangs_official')
# Install Library

try:
    import requests
    print("\n[OK]requests 已安装")
except ImportError:
    print("[X]requests未安装,正在安装")
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', 'requests', "-i", "https://mirrors.aliyun.com/pypi/simple/"])

try:
    import mutagen
    print("\n[OK]mutagen 已安装")
except ImportError:
    print("[X]utagen未安装,正在安装")
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', 'mutagen', "-i", "https://mirrors.aliyun.com/pypi/simple/"])

try:
    import yaml
    print("\n[OK]yaml 已安装")
except ImportError:
    print("[X]yaml未安装,正在安装")
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', 'pyyaml', "-i", "https://mirrors.aliyun.com/pypi/simple/"])

try:
    import colorlog
    print("\n[OK]colorlog 已安装")
except ImportError:
    print("[X]colorlog未安装,正在安装")
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', 'colorlog', "-i", "https://mirrors.aliyun.com/pypi/simple/"])

print("\n[OK]所有库安装完成")

# Write settings.yml

if not os.path.exists('settings.yml'):
    print("\n[...]正在生成设置文件")
    f = open("settings.yml", "w")
    f.close
    data = {'api_url': 'https://m163.a.vercel.stardawn.xyz/', 'use_cookie': False}
    with open('settings.yml', 'w', encoding='utf-8') as f:
        yaml.dump(data=data, stream=f, allow_unicode=True)
    print("\n[OK]生成settings.yml成功!")
else:
    print("\n[!]settings.yml已存在")

# Get Cookie
login_get_cookie = input("\n[?]要登录以获取Cookie吗(可以下载付费歌曲,如果你有会员的话),输入1获取,输入其他跳过:")
if login_get_cookie == "1":
    if not os.path.exists('cookie.txt'):
        print("\n[...]正在生成cookie.txt")
        f = open("cookie.txt", "w")
        f.close
    else:
        print("\n[!]已生成过cookie.txt")
    apiurl = 'https://m163.a.vercel.stardawn.xyz/'
    phone_code = input('\n[?]请输入您的账号（手机号码）：')
    countrycode = input('\n[?]输入国家码（中国填86）：')
    user_password = getpass.getpass('\n[?]请输入您的密码（不显示，输入后回车即可）：')
    time.sleep(1)
    print('\n[...]正在登录...')
    login_back = requests.get(
        apiurl + '/login/cellphone?phone=' + phone_code + '&password=' + user_password + '&countrycode=' + countrycode)
    if login_back.status_code == 200:
        origin_login_back_json = json.loads(login_back.text)
        cookie_value = origin_login_back_json.get("cookie")
        user_name = origin_login_back_json.get("profile", {}).get("nickname")
        with open("cookie.txt", "w") as ck_file:
            ck_file.write(cookie_value)
            print(f'\n[OK]欢迎您！{user_name}，登录成功,安装完毕,欢迎使用')
            exit()
    else:
        print('\n[!]出现错误!状态码：' + login_back.status_code + '\n返回内容：' + login_back.text + '\n 五秒后退出')
        time.sleep(5)
        exit()
else:
    print("\n[!]不选择登录,安装完毕,欢迎使用")
    exit()