##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：0
# 执行时间：2022-10-09 16:23:19
##################################################
import datetime
import time
import unittest

# from zypylibs.function.zycommon import updatecomment, updatedescribe  #
from icecream import ic


# def timestamp():
#     """返回时间戳

#     Returns:
#         _type_: _description_
#     """
#     return time.time()


def todatetime(val=None, fmt="%Y%m%d%H%M"):
    """将时间字符串转换为datetime对象\n
    示例:
        self.assertEqual(type(todatetime([])).__name__, 'NoneType')
        self.assertEqual(type(todatetime()).__name__, 'datetime')
        self.assertEqual(type(todatetime(totimestamp())).__name__, 'datetime')
        self.assertEqual(type(todatetime(int(totimestamp()))).__name__, 'datetime')
        self.assertEqual(type(todatetime('20110928105900', '%Y%m%d%H%M%S')).__name__, 'datetime')


    Args:
        val (_type_): _description_
        fmt (_type_): _description_

    Returns:
        _type_: _description_
    """
    valtype = type(val).__name__
    if valtype == "NoneType":
        return datetime.datetime.today()

    if valtype == "str":
        if len(val) == 14:
            return datetime.datetime.strptime(val, "%Y%m%d%H%M%S")
        if len(val) == 15:
            return datetime.datetime.strptime(val, "%Y%m%d_%H%M%S")
        if len(val) == 19 and "-" in val:
            return datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        if len(val) == 19 and "/" in val:
            return datetime.datetime.strptime(val, "%Y/%m/%d %H:%M:%S")
        return datetime.datetime.strptime(val, fmt)
    if valtype == "int":
        val = int(str(val)[0:10])
        return datetime.datetime.fromtimestamp(val)
    if valtype == "float":
        val = int(str(val)[0:10])
        return datetime.datetime.fromtimestamp(val)
    if valtype == "datetime":
        return val
    return None


def totimestamp(val=None, fmt2="%Y-%m-%d %H:%M:%S"):
    """时间戳转本地时间

    Args:
        val (_type_): _description_

    Returns:
        _type_: _description_
    """
    valtype = type(val).__name__
    # ic(valtype)
    if valtype == "NoneType":
        return time.time()
    if valtype == "str":
        return datetime.datetime.strptime(val, fmt2).timestamp()
    if valtype == "struct_time":
        return time.mktime(val)
    if valtype == "datetime":
        return val.timestamp()
    return None


def tostructtime(val=None, fmt="%Y%m%d%H%M"):
    valtype = type(val).__name__
    if val == None:
        return time.localtime()
    if valtype == "str":
        if len(val) == 14:
            return time.strptime(val, "%Y%m%d%H%M%S")
        if len(val) == 15:
            return time.strptime(val, "%Y%m%d_%H%M%S")
        if len(val) == 19 and "-" in val:
            return time.strptime(val, "%Y-%m-%d %H:%M:%S")
        if len(val) == 19 and "/" in val:
            return time.strptime(val, "%Y/%m/%d %H:%M:%S")
        return time.strptime(val, fmt)
    if valtype == "int":
        val = int(str(val)[0:10])
        return time.localtime(val)
    if valtype == "float":
        val = int(str(val)[0:10])
        return time.localtime(val)
    if valtype == "datetime":
        return time.localtime(val.timestamp())
    return None


def add(
    date=datetime.datetime.now(),
    fmt="%Y-%m-%d %H:%M:%S",
    fmt2="%Y-%m-%d %H:%M:%S",
    days=0,
    seconds=0,
):
    dt = todatetime(date, fmt)
    dt = dt + datetime.timedelta(seconds=seconds, days=days)
    return todatestring(dt, fmt2)


def todatestring(val=None, fmt="%Y-%m-%d %H:%M:%S", fmt2="%Y-%m-%d %H:%M:%S"):
    """_summary_

    Args:
        val (_type_): 传入支持格式:
            数字:时间戳
            字符串:支持14,15长度的解析
            时间类型:需要传入fmt2来
        fmt (str, optional): 格式化的字符串. Defaults to '%Y-%m-%d %H:%M:%S'.
        fmt2 (str, optional): 输入格式识别_description_. Defaults to ''.

    Returns:
        _type_: _description_
    """
    val = tostructtime(val, fmt2)
    if val == None:
        return None
    return time.strftime(fmt, val)


class zydate(unittest.TestCase):
    def test(self):
        # ic(type(todatetime()).__name__)
        # ic(type(totimestamp()).__name__)
        # ic(type(totimestamp('20110928105900', '%Y%m%d%H%M%S')).__name__)
        # ic(type(tostructtime()).__name__)
        # ic(type(datetime.datetime.now()).__name__)

        ic(todatetime().timestamp())
        # ic(time.time(tostructtime()))

    def test_add(self):
        self.assertEqual((todatestring(add(todatetime("20221009", fmt="%Y%m%d"), days=1), fmt="%Y%m%d")), "20221010",)
        self.assertEqual(type(todatestring(add(todatetime("20221009", fmt="%Y%m%d"), days=1), fmt="%Y%m%d")).__name__, "str",)
        self.assertEqual(type(todatestring(add(todatetime("20210528_234053"), days=1), fmt="%Y%m%d")).__name__,            "str",)
        self.assertEqual(add("20210528_234254", fmt2="%Y%m%d_%H%M%S", seconds=-120.04),           "20210528_234053",)

    def test_todatetime(self):
        self.assertEqual(type(todatetime([])).__name__, "NoneType")
        self.assertEqual(type(todatetime()).__name__, "datetime")
        self.assertEqual(type(todatetime(totimestamp())).__name__, "datetime")
        self.assertEqual(type(todatetime(int(totimestamp()))).__name__, "datetime")
        self.assertEqual(type(todatetime("20110928105900", "%Y%m%d%H%M%S")).__name__, "datetime")

    def test_totimestamp(self):
        self.assertEqual(type(totimestamp()).__name__, "float")
        # 测试字符串转时间戳
        self.assertEqual(type(totimestamp("20110928105900", "%Y%m%d%H%M%S")).__name__, "float")
        # 测试structtime转时间戳11111111111111111111111111111111111111111111111111111111111111111111111111111
        self.assertEqual(type(totimestamp(tostructtime())).__name__, "float")
        # 测试datetime时间戳
        self.assertEqual(type(totimestamp(todatetime())).__name__, "float")

    def test_tostructtime(self):
        self.assertEqual(type(tostructtime([])).__name__, "NoneType")
        self.assertEqual(type(tostructtime()).__name__, "struct_time")
        self.assertEqual(type(tostructtime("20110928105900", "%Y%m%d%H%M%S")).__name__, "struct_time")
        self.assertEqual(type(tostructtime(totimestamp())).__name__, "struct_time")

    def test_todatestring(self):
        # ic(todatestring(1673171105000))
        # ic(todatestring(1676351274.281531))
        # ic(todatestring(1665560939000))
        # ic(todatestring('20110928105900'))
        self.assertEqual(type(todatestring()).__name__, "str")
        self.assertEqual(type(todatestring([])).__name__, "NoneType")
        self.assertEqual(type(todatestring(1665560939)).__name__, "str")
        self.assertEqual(type(todatestring(int(totimestamp()))).__name__, "str")
        self.assertEqual(type(todatestring("20110928105900")).__name__, "str")
        self.assertEqual(type(todatestring("20110928_105900")).__name__, "str")
        self.assertEqual(type(todatestring("2011-09-28 10:59:00")).__name__, "str")
        self.assertEqual(type(todatestring("2011-09-28 10:59:00", fmt2="%Y-%m-%d %H:%M:%S")).__name__,            "str",)
        self.assertEqual(type(todatestring("2022/10/14 09:15:41")).__name__, "str")
        self.assertEqual(type(todatestring("2022/10/14 09:15:41", fmt2="%Y/%m/%d %H:%M:%S")).__name__,            "str",)


if __name__ == "__main__":
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()
