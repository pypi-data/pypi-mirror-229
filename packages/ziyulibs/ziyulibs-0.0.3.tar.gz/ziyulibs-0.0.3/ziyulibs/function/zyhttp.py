##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：0
# 执行时间：2023-01-07 22:09:12
##################################################
import json
import unittest
import urllib.request

import chardet
import requests
from bs4 import BeautifulSoup
from ziyulibs.base.zystr import unicodedecode
from ziyulibs.function.zylog import LOGTYPE, console, consoleErr


def geturldata(url, type=1):

    if type == 1:
        r = requests.get(url)
        return r.text

    if type == 2:
        data = urllib.request.urlopen(url).read()
        code = chardet.detect(data)['encoding']
        return data.decode(code)


def posturldata(url, data):
    r = requests.post(url, data)
    return r.text


class zyhttp(unittest.TestCase):
    def setUp(self) -> None:
        print('构建')
        console(label=LOGTYPE.调试, value=True)
        console(label=LOGTYPE.链接, value=True)
        console(label=LOGTYPE.配置, value=True)
        console(label=LOGTYPE.请求, value=True)
        console(label=LOGTYPE.语句, value=True)
        console(label=LOGTYPE.异常, value=True)
        return super().setUp()

    def tearDown(self) -> None:
        print('销毁')
        return super().tearDown()

    def test_geturldata(self):
        data = geturldata('http://127.0.0.1:5000//autoapi/tb0712_list?pagenum=2&pagesize=15', type=1)
        data = geturldata('http://127.0.0.1:5000//autoapi/tb0712_list?pagenum=2&pagesize=15', type=2)
        data = json.loads(data)['datalist']
        self.assertEqual(len(data), 15)

    def test_posturldata(self):
        data = posturldata('http://127.0.0.1:5000/autosql', {
            'code': 'tb0712_chart1',
            'data': json.dumps({})
        })
        data = json.loads(data)['datacount']
        self.assertEqual(data, 0)
        # print(unicodedecode(data))

# print(json.dumps(data, ensure_ascii=True))
# print(json.dumps(data, ensure_ascii=False))


if __name__ == '__main__':
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()
