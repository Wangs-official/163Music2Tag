#@author : Wangs_official
import os
import logging
import time
import json
import argparse
from logging.handlers import RotatingFileHandler

#Check
try:
    from colorlog import ColoredFormatter
    import requests
    import wget
    import yaml
    import mutagen
    from tqdm import tqdm
except ImportError as e:
    # Not install
    logging.error("[!] 库未完全安装,请执行 python install.py 重新安装,或者查看下方报错信息单独安装:pip install 库名")
    logging.error(e)
    exit()

#Something
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def progress_bar(current, total, width=80):
    progress = current / total * 100
    tqdm.write(f'下载中：{progress:.2f}% [共{total}字节]',end='\r')

#Set log
logger = logging.getLogger("163m2tag")
logger.setLevel(logging.DEBUG)
fmt = "%(log_color)s%(asctime)s %(log_color)s%(levelname)s %(log_color)s%(message)s"
datefmt = '%a, %d %b %Y %H:%M:%S'
formatter = ColoredFormatter(fmt=fmt,
                       datefmt=datefmt,
                       reset=True,
                       secondary_log_colors={},
                       style='%'
                       )
hd_1 = logging.StreamHandler()
hd_1.setFormatter(formatter)
logger.addHandler(hd_1)
logger.info("日志记录器加载完毕")
time.sleep(0.5)

#Check
if not os.path.exists('tmp'):
    logger.error("[!] tmp文件夹不存在,请创建tmp文件夹以及tmp/pics和tmp/songs文件夹")
    exit()
elif not os.path.exists("tmp/pics"):
    logger.error("[!] tmp/pics文件夹不存在,请创建tmp/pics文件夹")
    exit()
elif not os.path.exists("tmp/songs"):
    logging.error("[!] tmp/songs文件夹不存在,请创建tmp/songs文件夹")
    exit()
else:
    logger.info("缓存文件夹完整性检查完毕")

if not os.path.exists('settings.yml'):
    logger.error("[!] 配置文件不存在,请执行 python install.py 重新安装")
    exit()
else:
    logger.info("配置文件存在")
time.sleep(0.5)

#Load settings
try:
    with open('settings.yml') as f:
        y = yaml.safe_load(f)
        api_url = y['api_url']
        use_cookie = y['use_cookie']
        del_tmp = y['del_tmp_when_complete']
        use_cookie_s = str(use_cookie)
        del_tmp_s = str(del_tmp)
    f.close()
except KeyError as e:
    logger.error(f"配置文件异常,请执行 python install.py 重新安装:{e}")
    exit()
logger.info(f"配置文件加载完成! API地址:{api_url} , 是否使用Cookie:{use_cookie_s} , 是否在每次完成后删除缓存:{del_tmp}")
time.sleep(0.5)

#Create header
if use_cookie:
    if os.path.exists("cookie.txt"):
        with open("cookie.txt") as f:
            headers = {'Cookie': f.read()}
            logger.info("请求头构建完毕")
    else:
        logger.error("不存在cookie.txt文件,请将settings.yml内 use_cookie 的值改为 false 或者 执行 python install.py 重新安装")
        exit()
else:
    headers = {}
    logger.warning("不使用Cookie进行请求,将无法使用账号VIP下载音乐")
time.sleep(0.5)

# Start
parser = argparse.ArgumentParser(description='https://github.com/wangs-official/163Music2Tag/\nAuthor:Wangs_official')
parser.add_argument("-id", "--songid", help="The Song ID" , type=str , required=True)
args = parser.parse_args()
if is_number(args.songid):
    logger.info(f"歌曲ID:{args.songid},正在获取中")
    time.sleep(1)
    song_api_url = api_url + "song/url?id=" + args.songid
    songlrc_api_url = api_url + "lyric?id=" + args.songid
    songinfo_api_url = api_url + "song/detail?ids=" + args.songid
    logger.debug(f"\n{song_api_url},{songlrc_api_url},{songinfo_api_url}")
    song_req = requests.get(song_api_url , headers=headers)
    song_lrc_req = requests.get(songlrc_api_url)
    song_info_req = requests.get(songinfo_api_url)
    if song_req.status_code == 200:
        song_url = json.loads(song_req.text)['data'][0]['url']
        song_fti = json.loads(song_req.text)['data'][0]['freeTrialInfo']
        if song_url is None:
            logger.error("返回了一个null,可能是输入的ID错误")
            exit()
        try:
            if len(song_fti) > 0:
                logger.error("这是一个会员才能听的歌曲")
                exit()
        except TypeError:
            pass
        #Download
        logger.info(f"获取成功,正在下载")
        song_download_name = args.songid + ".mp3"
        try:
            wget.download(song_url, out='tmp/songs/' + song_download_name , bar=progress_bar)
        except Exception as e:
            logger.error(f'下载时出现异常: {e}')
    else:
        logging.error(f"请求出现异常\n状态码:{song_req.status_code}\n返回:{song_req.text}")
else:
    logger.error("输入的不是一个数字")
    exit()
