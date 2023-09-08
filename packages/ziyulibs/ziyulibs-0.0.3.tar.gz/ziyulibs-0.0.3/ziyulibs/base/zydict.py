##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：0
# 执行时间：2023-01-07 22:09:12
##################################################


# 把字典集合转换成一个字典
import json
import unittest
# from ziyulibs.function.zycommon import updatecomment, updatedescribe  #


def dictarr2dict(source, key='name', value='value'):
    dic1 = {}
    for item in source:
        key = (item['name'].lower())
        val = item['value']
        dic1[key] = val
    return dic1


def mergedict(data):
    """合并字典集合

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    return {k: v for d in data for k, v in d.items()}

# 两个数组合并成一个字典


def mappingdict(arr1, arr2):
    dic = {}
    for idx, item in enumerate(arr1):
        dic[item] = arr2[idx]

    return dic


def reversedict(olddict):
    """

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """

    # print(olddict.items())

    return {v: k for (k, v) in olddict.items()}

    # newdict = {}
    # for k, v in olddict.items():
    #     newdict[v] = k
    # return newdict

# def mergedict2(dict1, dict2):
#     # 方法1
#     dt1 = {'a': 1, 'b': 2}
#     dt2 = {'c': 3, 'd': 4}
#     dt3 = dict(**dt1, **dt2)
#     # dt3 = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

#     # 方法2
#     dt1 = {'a': 1, 'b': 2}
#     dt2 = {'c': 3, 'd': 4}
#     dt3 = dict(dt1, **dt2)
#     # dt3 = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

#     # 方法3
#     # class dict(iterable, **kwarg)
#     dt1 = {'a': 1, 'b': 2}
#     dt2 = {'c': 3, 'd': 4}
#     dt3 = dict(dt1.items(), **dt2)
#     # dt3={'a': 1, 'b': 2, 'c': 3, 'd': 4}

#     # 方法4
#     # class dict().update()
#     dt1 = {'a': 1, 'b': 2}
#     dt2 = {'c': 3, 'd': 4}
#     dt1.update(dt2)
#     # dt1={'a': 1, 'b': 2, 'c': 3, 'd': 4}


class zydict(unittest.TestCase):
    # def test_mergedict(self):
    #     result = mergedict([{'备用字段41': '10'}, {'备用字段42': '11'}])
    #     self.assertEqual(result, {'备用字段41': '10', '备用字段42': '11'})

    # def test__dictarr2dict(self):
    #     result = dictarr2dict([
    #         {
    #             "name": ":authority",
    #             "value": "www.jq22.com"
    #         },
    #         {
    #             "name": ":method",
    #             "value": "GET"
    #         },
    #         {
    #             "name": ":path",
    #             "value": "/demo/laydate201711030052/laydate/need/laydate.css"
    #         }
    #     ], 'name', 'value')
    #     # print(result)
    #     self.assertEqual(result, {
    #         ':authority': 'www.jq22.com',
    #         ':method': 'GET',
    #         ':path': '/demo/laydate201711030052/laydate/need/laydate.css'
    #     })

    def test__mappingdict(self):
        arr1 = ['GPS_纬度', 'GPS_经度', 'GPS_高度']
        arr2 = ['GPS_纬度', 'GPS_经度', 'GPS_高度']
        map = mappingdict(arr1, arr2)
        self.assertEqual(map, {
            'GPS_纬度': 'GPS_纬度',
            'GPS_经度': 'GPS_经度',
            'GPS_高度': 'GPS_高度'})

    def test__reversedict(self):
        dic1 = {
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
            'EXIF BrightnessValue': '高级照片_亮度',
            'EXIF LightSource': '高级照片_光源',
            'EXIF Contrast': '高级照片_对比度',
            'EXIF Saturation': '高级照片_饱和度',
            'EXIF Sharpness': '高级照片_清晰度',
            'EXIF WhiteBalance': '高级照片_白平衡',
        }

        map = reversedict(dic1)

        # print(json.dumps(map, indent=2, ensure_ascii=False))

        self.assertEqual(map, {
            'GPS_纬度': 'GPS GPSLatitude',
            'GPS_经度': 'GPS GPSLongitude',
            'GPS_高度': 'GPS GPSAltitude',
            '图像_宽度': 'Image ImageWidth',
            '图像_高度': 'Image ImageLength',
            '来源_拍摄时间': 'Image DateTime',
            '照相机_ISO速度': 'EXIF ISOSpeedRatings',
            '照相机_曝光时间': 'EXIF ExposureTime',
            '照相机_照相机制造商': 'Image Make',
            '照相机_照相机型号': 'Image Model',
            '高级照片_亮度': 'EXIF BrightnessValue',
            '高级照片_光源': 'EXIF LightSource',
            '高级照片_对比度': 'EXIF Contrast',
            '高级照片_清晰度': 'EXIF Sharpness',
            '高级照片_白平衡': 'EXIF WhiteBalance',
            '高级照片_饱和度': 'EXIF Saturation'
        })


if __name__ == '__main__':
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()
