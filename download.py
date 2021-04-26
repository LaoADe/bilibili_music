import os
import re
import requests
from mutagen.id3 import ID3, APIC, TIT2, TPE1
from pydub import AudioSegment
from io import BytesIO

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/79.0.3945.130 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive'
}


def get_html():
    uid = "431205710"
    i = 2
    e_url = []
    while i:
        StartSource = "https://api.bilibili.com/x/space/arc/search?mid=" + uid + "&ps=30&tid=3&pn=" + str(
            i) + "&keyword=&order=pubdate&jsonp=jsonp"
        i += 1
        content = requests.get(StartSource).json()
        e_url.append(StartSource)
        vlist = content["data"]["list"]["vlist"]
        download(vlist)
        if len(vlist) == 0:
            break


def download(vlist):
    for i in range(len(vlist)):
        title = vlist[i]["title"]
        pic_url = vlist[i]["pic"]
        pic = requests.get(pic_url, headers=headers).content
        img = BytesIO(pic).read()
        author = vlist[i]["author"]
        avid = vlist[i]["aid"]
        bvid = vlist[i]["bvid"]
        url = f"https://www.bilibili.com/video/{bvid}"
        headers2 = {
            'Accept-Encoding': 'identity',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': url,
            'Range': 'bytes=0-',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.130 Safari/537.36 '
        }

        html = requests.get(url, headers=headers).text
        if os.path.exists(author):
            info_mp3(author, headers2, html, i, title, img)
        else:
            os.makedirs(author)
            info_mp3(author, headers2, html, i, title, img)


def info_mp3(author, headers2, html, i, title, img):
    video_name = author + "/" + (
            title.replace('/', '／').replace('\\', '＼').replace('|', '_').replace('?', '？') + '.mp3').lstrip()
    print(video_name)
    print(re.findall('"audio":.*?"baseUrl":"(.*?)".*?}', html, re.S)[0])
    audio_url = re.findall('"audio":.*?"baseUrl":"(.*?)".*?}', html, re.S)[0]

    video_url = re.findall('window.__playinfo__={.*?"baseUrl":"(.*?)".*?}', html, re.S)[0]
    response = requests.get(audio_url, headers=headers2, stream=True, verify=False)
    song = AudioSegment.from_file(BytesIO(response.content))
    song.export(video_name, format="mp3")
    info = {'title': title, 'artist': author, "img": img}
    SetMp3Info(video_name, info)
    i += 1


def SetMp3Info(path, info):
    songFile = ID3(path)
    songFile.update_to_v24()
    songFile['APIC'] = APIC(  # 插入专辑图片
        encoding=0,
        mime='image/jpeg',
        type=3,
        data=info['img']
    )
    songFile['TIT2'] = TIT2(  # 插入歌名
        encoding=3,
        text=info['title']
    )
    songFile['TPE1'] = TPE1(  # 插入第一演奏家、歌手、等
        encoding=3,
        text=info['artist']
    )
    songFile.save()


if __name__ == "__main__":
    get_html()
