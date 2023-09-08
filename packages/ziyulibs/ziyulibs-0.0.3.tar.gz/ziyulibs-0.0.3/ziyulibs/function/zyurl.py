##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：0
# 执行时间：2023-01-07 22:09:12
##################################################
import unittest
import urllib.parse

from ziyulibs.function.zycommon import updatedescribe

# updatedescribe(__file__)


def urlencode(txt):
    '''
    编码
    '''
    # print('url编码：', urllib.parse.quote('我爱中国'))
    return urllib.parse.quote(txt)


def urldecode(txt):
    '''
    解码
    '''
    # print('url解码：', urllib.parse.unquote('%E7%AC%91%E5%82%B2%E6%B1%9F%E6%B9%96'))
    return urllib.parse.unquote(txt)


class zyurl(unittest.TestCase):
    def test_tostr(self):
        self.assertEqual(urlencode('我爱中国'), '%E6%88%91%E7%88%B1%E4%B8%AD%E5%9B%BD')

    def test_urldecode(self):
        self.assertEqual(urldecode('%E6%88%91%E7%88%B1%E4%B8%AD%E5%9B%BD'), '我爱中国')


if __name__ == '__main__':
    unittest.main()
