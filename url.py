# @author : Wangs_official
url = input("请输入URL，像这样：https://music.163.com/song?id=xxx&userid=xxx >>> ")
if len(url) == 0:
    exit('什么也不输是有什么心事吗')
else:
    url_1 = url.split('?')[1]
    url_2 = url_1.split('&')[0]
    id = url_2.split('=')[1]
    print(f'ID : {id}')
