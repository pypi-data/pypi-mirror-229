##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：0
# 执行时间：2023-01-07 22:09:12
##################################################
# import re
from pypinyin import pinyin, lazy_pinyin, Style

# from urllib import quote
import urllib.parse
import unittest
import base64

# from zypylibs.function.zycommon import updatecomment, updatedescribe  #

from deprecated.sphinx import deprecated


@deprecated(version="1.0", reason="This function will be removed soon")
def cut_text(txt: str, length: int):
    """按自定长度切割字符串

    Args:
        txt (_type_): _description_
        length (_type_): _description_

    Returns:
        _type_: _description_
    """
    txtarr = []
    zs = len(txt)
    zs2 = int(zs / length) if zs % length == 0 else int(zs / length) + 1
    for i in range(zs2):
        txtarr.append(txt[length * i : length * (i + 1)])
    return txtarr


def isChinese(word: str):
    """验证是否为中文

    Args:
        word (str): _description_

    Returns:
        boolean: 是否为中文
    """
    for ch in word:
        if "\u4e00" <= ch <= "\u9fff":
            return True
    return False


def toEnglish(word):
    """转为英文,例如:"中国"转为"zg"

    Args:
        word (_type_): _description_

    Returns:
        _type_: _description_
    """
    # return ''.join(list(map(lambda m: m[0][0].upper(), pinyin(word))))
    return "".join(lazy_pinyin(word, style=Style.FIRST_LETTER))


def urlencode(text):
    """页面文本编码,例如:"青春百战"转为"%E9%9D%92%E6%98%A5%E7%99%BE%E6%88%98"

    Args:
        text (_type_): _description_

    Returns:
        _type_: _description_
    """
    return urllib.parse.quote(text)


def urldecode(text):
    """页面文本解码,例如:"%E9%9D%92%E6%98%A5%E7%99%BE%E6%88%98"转为"青春百战"

    Args:
        text (_type_): _description_

    Returns:
        _type_: _description_
    """
    # test = "微信公众账号比特量化"
    # print(test)
    # new = urllib.parse.quote(test)
    # print(new)
    # print(urllib.parse.unquote(new))
    return urllib.parse.unquote(text)


def base64encode(text, encoding="utf8"):
    """base64编码,例如:"青春百战"转为"6Z2S5pil55m+5oiY"

    Returns:
        _type_: _description_
    """
    # return base64.b64encode(text.encode('utf-8'))

    strEncode = base64.b64encode(text.encode(encoding))
    return str(strEncode, encoding)


def base64decode(text, encoding="utf8"):
    """base64解码,例如:"6Z2S5pil55m+5oiY"转为"青春百战"

    Args:
        text (_type_): _description_
        encoding (str, optional): _description_. Defaults to "utf8".

    Returns:
        _type_: _description_
    """
    # return base64.b64decode(text).decode()
    strDecode = base64.b64decode(bytes(text, encoding=encoding))
    return str(strDecode, encoding)


def unicodeencode(text, encoding="unicode_escape"):
    """unicode编码,例如:"青春百战"转为"\\\\u9752\\\\u6625\\\\u767e\\\\u6218"

    Args:
        text (_type_): _description_
        encoding (str, optional): _description_. Defaults to "unicode_escape".

    Returns:
        _type_: _description_
    """
    return text.encode(encoding)


def unicodedecode(text, encoding="unicode_escape"):
    """unicode解码,例如:"\\\\u9752\\\\u6625\\\\u767e\\\\u6218"转为"青春百战"

    Args:
        text (_type_): _description_
        encoding (str, optional): _description_. Defaults to "unicode_escape".

    Returns:
        _type_: _description_
    """
    if type(text).__name__ == "str":
        text = text.encode("utf-8")
    return text.decode(encoding)


def checkidcard(IDCARD: str = "210303198906252513"):
    """验证是否为合格的身份证格式

    Args:
        IDCARD (str, optional): 身份证号. 默认为 "210303198906252513".

    Returns:
        Boolean: 是否合格
    """
    count = 0
    for idx, item in enumerate(IDCARD):
        # print(idx, item,  [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2, 0][idx])
        count = (
            count
            + int(item) * [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2, 0][idx]
        )
        # print(count)

    # print(count)
    # print(count % 11)

    # mapping1 =
    # print(len(mapping1))
    # print(mapping1[count % 11])
    return ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"][count % 11]


class zystr(unittest.TestCase):
    def test_isChinese(self):
        self.assertEqual(isChinese("中国"), True)
        self.assertEqual(isChinese("123"), False)
        self.assertEqual(isChinese("AA"), False)
        self.assertEqual(isChinese("中国AA"), True)

    def test_toEnglish(self):
        self.assertEqual(toEnglish("中国"), "zg")
        self.assertEqual(toEnglish("123"), "123")
        self.assertEqual(toEnglish("AABA"), "AABA")
        self.assertEqual(toEnglish("中国123"), "zg123")

    def test_urlencode(self):
        self.assertEqual(urlencode("青春百战"), "%E9%9D%92%E6%98%A5%E7%99%BE%E6%88%98")

    def test_urldecode(self):
        self.assertEqual(urldecode("%E9%9D%92%E6%98%A5%E7%99%BE%E6%88%98"), "青春百战")

    def test_base64encode(self):
        self.assertEqual(base64encode("青春百战"), "6Z2S5pil55m+5oiY")
        self.assertEqual(base64encode("青春百战", encoding="gbk"), "x+C0urDZ1b0=")

    def test_base64decode(self):
        self.assertEqual(base64decode("6Z2S5pil55m+5oiY"), "青春百战")
        self.assertEqual(base64decode("x+C0urDZ1b0=", encoding="gbk"), "青春百战")
        print(base64decode("bG1kV29hbmZTS2txVVNCSWZSZjNlUT09", encoding="gbk"))
        print(base64decode("bG1kV29hbmZTS2txVVNCSWZSZjNlUT09", encoding="utf8"))

    def test_unicodeencode(self):
        self.assertEqual(unicodeencode("青春百战"), b"\u9752\u6625\u767e\u6218")
        self.assertEqual(unicodeencode("青春百战"), b"\\u9752\\u6625\\u767e\\u6218")
        self.assertEqual(
            unicodeencode("青春百战", encoding="utf8"),
            b"\xe9\x9d\x92\xe6\x98\xa5\xe7\x99\xbe\xe6\x88\x98",
        )
        self.assertEqual(
            unicodeencode("青春百战", encoding="gbk"), b"\xc7\xe0\xb4\xba\xb0\xd9\xd5\xbd"
        )
        # self.assertEqual(unicodeencode('青春百战', encoding='utf8'),  b'\\xe9\\x9d\\x92\\xe6\\x98\\xa5\\xe7\\x99\\xbe\\xe6\\x88\\x98') #错误

    def test_unicodedecode(self):
        self.assertEqual(unicodedecode(b"\u9752\u6625\u767e\u6218"), "青春百战")
        self.assertEqual(unicodedecode(r"\u9752\u6625\u767e\u6218"), "青春百战")
        self.assertEqual(unicodedecode("\\u9752\\u6625\\u767e\\u6218"), "青春百战")

    def test_checkidcard(self):
        self.assertEqual(checkidcard("210303198906252513"), "3")


if __name__ == "__main__":
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()
