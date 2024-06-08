# @author : Wangs_official
import argparse
import json
import logging
import os
import ssl
import time

# Check
try:
    from colorlog import ColoredFormatter
    from mutagen.id3 import ID3, TIT2, TALB, TPE1, TCOM, APIC
    from mutagen.id3 import ID3NoHeaderError
    from mutagen.id3 import USLT, Encoding
    from tqdm import tqdm
    import requests
    import wget
    import yaml
except ImportError as e:
    # Not install
    logging.error("[!] 库未完全安装,请执行 python install.py 重新安装,或者查看下方报错信息单独安装:pip install 库名")
    logging.error(e)
    exit()


# Something
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
    ft = '{:.2f}'.format(total / 1048576)
    tqdm.write(f'下载中：{progress:.2f}% [共{ft}Mb]', end='\r')


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Set log
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

# Check
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
    logger.info("配置文件检查完毕")

if not os.path.exists('output'):
    logger.error("[!] output文件夹不存在,请创建output文件夹")
    exit()
else:
    logger.info("输出文件夹检查完毕")
time.sleep(0.5)

# Load settings
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

# Create header
if use_cookie:
    if os.path.exists("cookie.txt"):
        with open("cookie.txt") as f:
            headers = {'Cookie': f.read()}
            logger.info("请求头构建完毕")
    else:
        logger.error(
            "不存在cookie.txt文件,请将settings.yml内 use_cookie 的值改为 false 或者 执行 python install.py 重新安装")
        exit()
else:
    headers = {}
    logger.warning("不使用Cookie进行请求,将无法使用账号VIP下载音乐")
time.sleep(0.5)

# Start
parser = argparse.ArgumentParser(description='https://github.com/wangs-official/163Music2Tag/\nAuthor:Wangs_official')
parser.add_argument("-id", "--songid", help="The Song ID", type=str, required=True)
args = parser.parse_args()
start_time = int(time.time())
spl_songid = args.songid.split(',')
allid = str(len(spl_songid))
for sid in range(len(spl_songid)):
    if is_number(spl_songid[sid]):
        logger.info(f"歌曲ID:{spl_songid[sid]},正在获取中(第{sid + 1}/{allid}个)")
        time.sleep(1)
        song_api_url = api_url + "song/url?id=" + spl_songid[sid]
        songlrc_api_url = api_url + "lyric?id=" + spl_songid[sid]
        songinfo_api_url = api_url + "song/detail?ids=" + spl_songid[sid]

        song_req = requests.get(song_api_url, headers=headers)
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
            # Download
            song_download_name = spl_songid[sid] + ".mp3"
            try:
                if os.path.exists(f"tmp/songs/{song_download_name}"):
                    logger.warning("目录下已有此歌曲文件,默认删除重下")
                    os.remove(f"tmp/songs/{song_download_name}")
                time.sleep(0.3)
                wget.download(song_url, out='tmp/songs/' + song_download_name, bar=progress_bar)
                logger.info(f"歌曲下载成功")
            except Exception as e:
                logger.error(f'下载时出现异常: {e}')
                exit()
        else:
            logging.error(f"请求出现异常\n状态码:{song_req.status_code}\n返回:{song_req.text}")
            exit()

        song_info_req = requests.get(songinfo_api_url)
        if song_info_req.status_code == 200:
            song_info_j = json.loads(song_info_req.text)
            _song_name = song_info_j['songs'][0]['name']
            _song_al_name = song_info_j['songs'][0]['al']['name']
            _song_al_pic_adrori = song_info_j['songs'][0]['al']['picUrl']
            _song_al_pic = "http://" + _song_al_pic_adrori.split("https://")[1]
            _song_artist_origin = song_info_j['songs'][0]['ar']
            _song_artist_0 = [artist["name"] for artist in _song_artist_origin]
            _song_artist = ",".join(_song_artist_0)
            logger.info(f"歌曲名:{_song_name} , 歌手:{_song_artist} , 专辑:{_song_artist}")
            # Download
            songpic_download_name = spl_songid[sid] + ".jpg"
            try:
                if os.path.exists(f"tmp/pics/{songpic_download_name}"):
                    logger.warning("目录下已有此专辑图片,默认删除重下")
                    os.remove(f"tmp/pics/{songpic_download_name}")
                time.sleep(0.3)
                wget.download(_song_al_pic, out='tmp/pics/' + songpic_download_name, bar=progress_bar)
                logger.info(f"专辑图片下载成功")
            except Exception as e:
                logger.error(f'下载时出现异常: {e}')
                exit()
        else:
            logging.error(f"请求出现异常\n状态码:{song_req.status_code}\n返回:{song_req.text}")
            exit()

        # Mutagen
        try:
            tags = ID3('tmp/songs/' + song_download_name)
        except ID3NoHeaderError:
            tags = ID3()
        logger.info("开始打标签咯~")
        tags["TIT2"] = TIT2(encoding=3, text=_song_name)
        logger.info(f"歌曲名称:{_song_name}")
        time.sleep(0.5)
        tags["TALB"] = TALB(encoding=3, text=_song_al_name)
        logger.info(f"歌曲专辑名:{_song_al_name}")
        time.sleep(0.5)
        tags["TPE1"] = TPE1(encoding=3, text=_song_artist)
        tags["TCOM"] = TCOM(encoding=3, text=_song_artist)
        logger.info(f"歌手:{_song_artist}")
        time.sleep(0.5)
        _song_al_f = open("tmp/pics/" + songpic_download_name, 'rb')
        tags["APIC"] = APIC(encoding=0, mime='image/jpeg', type=3, desc=u'Cover', data=_song_al_f.read())
        tags.save()
        _song_al_f.close()
        logger.info("标签写入成功!")
        time.sleep(1)
        os.rename('tmp/songs/' + song_download_name, 'tmp/songs/' + _song_name + '.mp3')
        if os.path.exists(_song_name + '.mp3'):
            logger.warning("目录下已有此歌曲文件,默认删除")
            os.remove(f"output/{songpic_download_name}.mp3")
        os.rename('tmp/songs/' + _song_name + '.mp3', 'output/' + _song_name + '.mp3')
        logger.info("已将歌曲转到output文件夹")
        time.sleep(0.5)
        if del_tmp:
            os.remove('tmp/pics/' + songpic_download_name)
            logger.info("缓存已清理")
            use_time = str(int(time.time()) - start_time)
            logger.info(f"耗时{use_time}s")
        else:
            use_time = str(int(time.time()) - start_time)
            logger.warning("未设置缓存清理,跳过")
            logger.info(f"耗时{use_time}s")
    else:
        logger.error("输入的某个ID不是一个数字")
        exit()

use_time = str(int(time.time()) - start_time)
logger.info(f"工作完成,耗时{use_time}s,感谢使用,开源地址:https://github.com/Wangs-official/163Music2Tag")
exit()
