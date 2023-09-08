##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：1
# 执行时间：2023-01-27 17:13:51
##################################################
import json
import unittest

import cv2
import exifread
import eyed3
from moviepy.editor import VideoFileClip
from pymediainfo import MediaInfo
from zypylibs.function.zycommon import updatedescribe

# updatedescribe(__file__)

# pip install pymediainfo -i https://pypi.tuna.tsinghua.edu.cn/simple
# pip install eyed3 -i https://pypi.tuna.tsinghua.edu.cn/simple


def attrs(cls):

    for idx, item in enumerate(dir(cls)):
        # for idx, item in enumerate(cls.__dir__):
        if ('_' in item):
            continue
        # 跳过函数
        if (hasattr(cls[item], '__call__')):
            continue

        # print(idx, item, cls.__getattribute__(item))
        # if '_' not in item:
        # content = str(contents[item]) if item in contents else '--'
        # content = content if len(content) < 100 else str(len(content))
        # # print(len(content))
        # print(item + ':'+content)


# '__getattribute__'


def getimageinfo(path):
    def _convert_gps(coord_arr):
        arr = str(coord_arr).replace('[', '').replace(']', '').split(', ')
        d = float(arr[0])
        m = float(arr[1])
        s = float(arr[2].split('/')[0]) / float(arr[2].split('/')[1])
        return float(d) + (float(m) / 60) + (float(s) / 3600)

    info = {}
    maps = {
        'Image DateTime': '来源_拍摄时间',
        'Image ImageWidth': '图像_宽度',
        'Image ImageLength': '图像_高度',
        'GPS GPSLatitude': 'GPS_纬度',
        'GPS GPSLongitude': 'GPS_经度',
        'GPS GPSAltitude': 'GPS_高度',

        'Image Make': '照相机_照相机制造商',
        'Image Model': '照相机_照相机型号',
        'EXIF ExposureTime': '照相机_曝光时间',
        'EXIF ISOSpeedRatings': '照相机_ISO速度',
        # 'Image XResolution': '72',
        # 'Image YResolution': '72',
        'EXIF BrightnessValue': '高级照片_亮度',
        'EXIF LightSource': '高级照片_光源',
        'EXIF Contrast': '高级照片_对比度',
        'EXIF Saturation': '高级照片_饱和度',
        'EXIF Sharpness': '高级照片_清晰度',
        'EXIF WhiteBalance': '高级照片_白平衡',
    }
    f = open(path, 'rb')
    contents = exifread.process_file(f)
    f.close()
    for item in maps:
        if (item in ['GPS GPSLatitude', 'GPS GPSLongitude']):
            info[maps[item] + '_转换'] = str(_convert_gps(contents[item].printable)) if item in contents else '0'
        info[maps[item]] = str(contents[item]) if item in contents else ''
    return info


# 获取图片信息
_map = {
    '标题': 'title',
    '艺术家': 'artist',
    '唱片集': 'album',
    '年份': 'recording_date',
    '音轨号': 'track_num',
    '流派': 'genre',
    '注释': 'comments',
    '专辑集艺术家': 'album_artist',
    # '作曲家': 'composer'
    # 'CD号': 'disc_num'
}


def getmusicinfo(path):
    info = {}

    audiofile = eyed3.load(path)
    # print(audiofile)
    # print(audiofile.tag)
    # print('####', audiofile.tag.title)
    # print('####', audiofile.tag.__getattribute__('title'))
    # print(audiofile.tag.__dict__)
    # print(audiofile.tag.__dir__)
    # attrs(audiofile.tag)
    # (dir(audiofile.tag))
    for k, v in _map.items():
        # print(k, v)
        if(not hasattr(audiofile.tag, v)):
            print('缺少属性'+v)
            continue

        value = audiofile.tag.__getattribute__(v)
        if(not isinstance(value, str) and not isinstance(value, int)):
            continue

        try:
            info[k] = value
            info[v] = value
        except Exception as ex:
            print('无法获取' + k)
    # info['标题'] = audiofile.tag.title
    # info['艺术家'] = audiofile.tag.artist
    # info['唱片集'] = audiofile.tag.album
    # info['年份'] = audiofile.tag.recording_date
    # info['音轨号'] = audiofile.tag.track_num
    # print('genre' in audiofile.tag)
    # info['流派']= audiofile.tag.genre
    # info['注释']= audiofile.tag.comments
    # info['专辑集艺术家']= audiofile.tag.album_artist
    # info['作曲家']= audiofile.tag.composer
    # info['CD号']= audiofile.tag.disc_num
    return info
# 获取音频信息


def setmusicinfo(path, mapobj):
    audiofile = eyed3.load(path)
    for item in mapobj.items():
        print(item)
        if(item in _map):
            audiofile[item] = mapobj[item]
    # audiofile.tag.title = '酒醉的蝴蝶'  # 标题
    # # audiofile.tag.artist = '周杰伦'  # 艺术家
    # # audiofile.tag.album = '叶惠美'  # 唱片集
    # # audiofile.tag.recording_date = '2003'  # 年份
    # # audiofile.tag.track_num = 3  # 音轨号
    # # audiofile.tag.genre = 'Pop'  # 流派
    # # audiofile.tag.comments.set('Hello World!')  # 注释
    # # audiofile.tag.album_artist = '周杰伦'  # 专辑集艺术家
    # # audiofile.tag.composer = '周杰伦'  # 作曲家
    # # audiofile.tag.disc_num = 3  # CD号
    # # audiofile.tag.images.set(type_=3, img_data=open('cover.jpg', 'rb').read(), mime_type='image/jpeg')  # 封面
    # audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')


def getvideoinfo1(path):
    # info = {}
    media_info = MediaInfo.parse(path)
    data = media_info.to_json()
    data = json.loads(data)
    data = list(filter(lambda f: f['track_type'] == 'Video', data['tracks']))
    # print('####################', len(data))
    if(len(data) > 1):
        raise('信息过多')
    data = data[0]
    # print(data)
    info = {
        'width': data['width'],
        'height': data['height'],
        # 'start': data['start'],
        # 'end': data['end'],
        'duration': data['duration'],
        # 'fps': data['fps'],
    }
    # print(json.dumps(info, indent=2, ensure_ascii=False))
    return info


def getvideoinfo2(path):
    info = {}
    data = VideoFileClip(path)
    # print(data.__dict__)
    info['width'] = data.w
    info['height'] = data.h
    info['start'] = data.start
    info['end'] = data.end
    info['duration'] = data.duration
    info['fps'] = data.fps
    # info['size'] = data.size
    info['rotation'] = data.rotation
    return info


def getvideoinfo3(path):
    info = {}
    data = cv2.VideoCapture(path)
    # print(dir(data))
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    # 常用属性
    info = {
        # 视频文件的当前（播放）位置, 以毫秒为单位。 (1秒 =1000 毫秒)
        'CAP_PROP_POS_MSEC': (data.get(cv2.CAP_PROP_POS_MSEC)),
        # 基于以 0 开始的被捕获或解码的帧索引
        'CAP_PROP_POS_FRAMES': (data.get(cv2.CAP_PROP_POS_FRAMES)),
        # 在视频流的帧的宽度
        'width': (data.get(cv2.CAP_PROP_FRAME_WIDTH)),
        # 在视频流的帧的高度
        'height':  (data.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        # 帧速率
        'fps': (data.get(cv2.CAP_PROP_FPS)),
        # 帧总数
        'CAP_PROP_FRAME_COUNT': (data.get(cv2.CAP_PROP_FRAME_COUNT)),
        # 视频时长 (秒)
        'duration': (data.get(cv2.CAP_PROP_FRAME_COUNT) / data.get(cv2.CAP_PROP_FPS))
    }
    return info
# 获取视频信息


class zyfileinfo(unittest.TestCase):
    imagepath = r'H:\img\#删除\IMG_20220701_115812.jpg'
    musicpath = r'C:\0000\31web\ZyWeb\songs\酒醉的蝴蝶.mp3'  # r'C:\Users\86186\Desktop\20230102整理\离别的车站.mp3'
    videopath = r'D:\行车记录\202206\Recfront_20220603_153622.ts'

    # def test_getimageinfo(self):
    #     info1 = getimageinfo(self.imagepath)
    #     print(json.dumps(info1, indent=2, ensure_ascii=False))
    #     self.assertEqual(info1['来源_拍摄时间'], '2022:07:01 11:58:12')
    #     self.assertEqual(info1['图像_宽度'], '3648')
    #     self.assertEqual(info1['图像_高度'], '2736')

    def test_getmusicinfo(self):
        info1 = getmusicinfo(self.musicpath)
        # print(info1)
        # print(json.dumps(info1, indent=2, ensure_ascii=False))
        self.assertEqual(info1['title'], '酒醉的蝴蝶')
        self.assertEqual(info1['标题'], '酒醉的蝴蝶')
        self.assertEqual(info1['艺术家'], '崔伟立')

    # def test_getvideoinfo(self):
    #     info1 = getvideoinfo1(self.videopath)
    #     # print(json.dumps(info1, indent=2, ensure_ascii=False))
    #     # info2 = getvideoinfo2(self.videopath)
    #     # print(json.dumps(info2, indent=2, ensure_ascii=False))
    #     # info3 = getvideoinfo3(self.videopath)
    #     # print(json.dumps(info3, indent=2, ensure_ascii=False))
    #     self.assertEqual(info1['width'], 1920)
    #     self.assertEqual(info1['height'], 1080)
    #     self.assertEqual(info1['duration'], 120011)
    #     # self.assertEqual(info1['width'], info2['width'])
    #     # self.assertEqual(info1['height'], info2['height'])
    #     # self.assertEqual(info1['duration'], info2['duration'])


if __name__ == '__main__':
    unittest.main()
