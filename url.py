# @author : Wangs_official
mode = input("单个ID请输入1,多个输入2 >>> ")
if mode == '1':
    url = input("请输入URL，像这样：https://music.163.com/song?id=xxx&userid=xxx >>> ")
    if len(url) == 0:
        exit('什么也不输是有什么心事吗')
    else:
        url_1 = url.split('?')[1]
        url_2 = url_1.split('&')[0]
        id = url_2.split('=')[1]
        print(f'ID : {id}')
elif mode == '2':
    id = ''
    url = input("请输入URL，像这样：https://music.163.com/song?id=xxx&userid=xxx ，用空格隔开每一个链接>>> ").split(' ')
    if len(url) == 0:
        exit('什么也不输是有什么心事吗')
    else:
        for i in range(len(url)):
            url_1 = url[i].split('?')[1]
            url_2 = url_1.split('&')[0]
            id = id + url_2.split('=')[1] + ','
        print(f'ID : {id}')
else:
    exit('?')
