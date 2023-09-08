##################################################
# 功能说明：公共类
# 更新日期：
# 更新次数：
# 完成情况：99%
# 执行次数：124
# 执行时间：2023-01-27 17:48:14
##################################################
from zypylibs.function.zysqlite import (
    createdb,
    insertdb1,
    query,
    querydb,
    execute,
    createparams,
)  # querydb,
from zypylibs.function.zyfile import readfileauto, writefile
import unittest
import time
import re

# from zypylibs.function.zylog import console, consoleErr, LOGTYPE


def updatecomment(filename, isaddnew=True):
    """更新文件注释1111

    Args:
        filename (_type_): _description_
    """
    filelines = readfileauto(filename, isline=True)
    filelinelist = []
    # 整文件方式读取不行, 得不到行号 那就要配置autopep8的--max-line-length

    for lineno, fileline in enumerate(filelines):
        fileline = fileline.replace("\n", "")
        consoles = re.findall("(console\(.*?\)$)", fileline)
        # 没有console则跳过
        if len(consoles) <= 0:
            filelinelist.append(fileline)
            continue
        # 多个console则报错
        if len(consoles) > 1:
            print("console只能有一个")

        # 这里其实只有一个，可以通过索引来取
        # console = consoles[0]
        for console in consoles:
            newconsole = ""
            positions = re.findall("(position=('.*'))", console)
            print(positions)
            # 没有positions则新增,开关控制
            if len(positions) == 0 and isaddnew:
                newconsole = (
                    console[:-1]
                    + ", position='"
                    + filename
                    + ":"
                    + str(lineno + 1)
                    + "')"
                )
            # 一个positions曾替换
            if len(positions) == 1:
                newconsole = console.replace(
                    positions[0][1], "'" + filename + ":" + str(lineno + 1) + "'"
                )
            # 多个positions则报错
            if len(positions) > 1:
                print("position只能有一个")

            # 替换fileline中的console
            fileline = fileline.replace(console, newconsole)

        filelinelist.append(fileline)
    # 拼接保存
    writefile(filename, "\n".join(filelinelist))


def updatedescribe(filename, isexec=True):
    """更新文件描述

    Args:
        filename (_type_): _description_

    Raises:
        ex: _description_
    """
    memokeys = {"功能说明": "", "更新日期": "", "更新次数": "", "完成情况": "", "执行次数": "0", "执行时间": ""}
    try:
        filetxt = readfileauto(filename)
        filememo = re.findall("#{50}[\S\s]*?#{50}", filetxt)
        oldmemo = filememo[0] if len(filememo) > 0 else ""

        newmemo = "#" * 50 + "\n"
        execname = ""
        execmemo = ""
        exectime = ""
        execnums = ""
        for idx, item in enumerate(memokeys.keys()):
            value = memokeys[item]  # 默认值
            filememo1 = re.findall(item + "：(\S*)", oldmemo)
            if len(filememo1) > 0:
                value = ";".join(filememo1)
            if item == "功能说明":
                execname = value
            if item == "完成情况":
                execmemo = value
            if item == "执行次数":
                try:
                    value = str(int(filememo1[0]) + (1 if isexec else 0))
                except:
                    value = "0"
                execnums = value
            if item == "执行时间":
                value = time.strftime("%Y-%m-%d %H:%M:%S")
                exectime = value
            newmemo = newmemo + "# " + item + "：" + value + "\n"
        newmemo = newmemo + "#" * 50

        filedesc = re.findall("updatedescribe\(.*\)", filetxt)
        print(filedesc, filename, isexec)
        if len(filedesc) <= 0:
            newmemo = (
                newmemo
                + """
from zypylibs.function.zycommon import updatedescribe
"""
            )
        if len(oldmemo) == 0:
            filetxt = newmemo + "\n" + filetxt
        else:
            filetxt = filetxt.replace(oldmemo, newmemo)
        # writefile(filename, filetxt)

        # print(filename, exectime, execnums, execname, execmemo)
        # if isexec:
        #     createdb(
        #         r"C:\0000\54sqlite\zysqlite\zysqlite.db",
        #         "tb0193",
        #         ["文件名称", "执行时间", "执行次数", "功能说明", "完成情况"],
        #     )
        #     insertdb1(
        #         r"C:\0000\54sqlite\zysqlite\zysqlite.db",
        #         "tb0193",
        #         ["文件名称", "执行时间", "执行次数", "功能说明", "完成情况"],
        #         [(filename, exectime, execnums, execname, execmemo)],
        #     )
        return {
            "filename": filename,
            "exectime": exectime,
            "execnums": execnums,
            "execname": execname,
            "execmemo": execmemo,
            "descnums": len(filedesc),
        }
    except Exception as ex:
        print("zypylibs->updatedescribe异常:" + str(ex))
        raise ex


class zycommon(unittest.TestCase):
    # def setUp(self) -> None:
    #     # print('构建')
    #     # console(label=LOGTYPE.调试, value=True, position='C:\0000\47python\zypylibs\zypylibs\function\zycommon.py:138')
    #     # console(label=LOGTYPE.链接, value=True, position='C:\0000\47python\zypylibs\zypylibs\function\zycommon.py:139')
    #     # console(label=LOGTYPE.配置, value=True, position='C:\0000\47python\zypylibs\zypylibs\function\zycommon.py:140')
    #     # console(label=LOGTYPE.请求, value=True, position='C:\0000\47python\zypylibs\zypylibs\function\zycommon.py:141')
    #     # console(label=LOGTYPE.语句, value=True, position='C:\0000\47python\zypylibs\zypylibs\function\zycommon.py:142')
    #     # console(label=LOGTYPE.异常, value=True, position='C:\0000\47python\zypylibs\zypylibs\function\zycommon.py:143')
    #     # console(111111111111111, label=LOGTYPE.调试, value=True,, position='C:\0000\47python\zypylibs\zypylibs\function\zycommon.py:144')
    #     # console(json.dump({}), label=LOGTYPE.调试, value=True, position='C:\0000\47python\zypylibs\zypylibs\function\zycommon.py:145')
    #     return super().setUp()

    # def tearDown(self) -> None:
    #     return super().tearDown()

    def test_updatecomment(self):
        updatecomment(__file__)

    def test_updatedescribe(self):
        updatedescribe(__file__)


if __name__ == "__main__":
    unittest.main()
