##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：0
# 执行时间：2023-01-07 22:09:12
##################################################
import struct
import unittest

# int(x [,base ])         将x转换为一个整数
# long(x [,base ])        将x转换为一个长整数
# float(x )               将x转换到一个浮点数
# complex(real [,imag ])  创建一个复数
# str(x )                 将对象 x 转换为字符串
# repr(x )                将对象 x 转换为表达式字符串
# eval(str )              用来计算在字符串中的有效Python表达式,并返回一个对象
# tuple(s )               将序列 s 转换为一个元组
# list(s )                将序列 s 转换为一个列表
# chr(x )                 将一个整数转换为一个字符
# unichr(x )              将一个整数转换为Unicode字符
# ord(x )                 将一个字符转换为它的整数值
# hex(x )                 将一个整数转换为一个十六进制字符串
# oct(x )                 将一个整数转换为一个八进制字符串

# struct.pack
# struct的pack函数把任意数据类型变成bytes

# struct.unpack
# unpack把bytes变成相应的Python数据类型


def tobyte(m):
    """字符串转字节
    先转成16进制数字,然后转换为字节

    Args:
        data (_type_): 数组集合

    Returns:
        _type_: _description_
    """
    # print(m)
    # print(int(str(m), 16))
    return struct.pack('B', int(str(m), 16))


def tobyte2(m):
    """字符转字节

    Args:
        data (_type_): 数组集合

    Returns:
        _type_: _description_
    """
    # print(m)
    # print(type(m))
    # print(int(str(m), 16))
    # print(ord('A'))  # 65
    # print(hex(ord('A')))  # 0x41
    # return hex(ord('A'))
    return hex(ord(m))


def tostr(data):
    """字节转字符串

    Args:
        data (_type_): 数组集合

    Returns:
        _type_: _description_
    """
    # 转换为数字
    dataint = struct.unpack('B', data)[0]
    # print(dataint)
    # 1.转换为16进制数字
    # 2.转换为字符串
    # 3.替换掉'0x'
    # 4.补零
    datahex = str(hex(dataint)).replace('0x', '').rjust(2, '0')
    return datahex


class zybyte(unittest.TestCase):
    def test_tobyte(self):
        self.assertEqual(tobyte('23'), b'#')

    def test_tobyte2(self):
        self.assertEqual(tobyte2('B'), '0x42')

    def test_tostr(self):
        # self.assertEqual(tostr(b'P'), '50')
        self.assertEqual(tostr(b'N'), '4e')


if __name__ == '__main__':
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()

