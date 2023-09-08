##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：117
# 执行时间：2023-01-07 22:09:12
##################################################
from enum import Enum
import json
import unittest
# from zypylibs.function.zycommon import updatecomment, updatedescribe
# import ..common
# 测试文件 47python\demo2207\demo2022082411.py
# isprintdebug = False
# isprinterror = True


class LOGTYPE(Enum):
    # 异常链接 = '\033[4;37;41m%s\033[0m'  # _白_/_红_
    无 = '\033[0m%s'
    调试 = '\033[0;37;43m%s\033[0m'  # 白/黄
    链接 = '\033[1;37;40m%s\033[0m'  # #_白_/_黑_

    配置 = '\033[0;37;47m%s\033[0m'  # 白/白
    请求 = '\033[0;37;42m%s\033[0m'  # 白/绿
    语句 = '\033[0;37;44m%s\033[0m'  # 白/蓝
    异常 = '\033[1;37;41m%s\033[0m'  # 白/红


consoleconfig = {
    '无': False,
    '位置': True,

    '调试': False,
    '链接': False,

    '配置': False,
    '请求': False,
    '语句': False,
    '异常': True
}


class VALTYPE(Enum):
    str = 'str'
    int = 'int'
    float = 'float'
    bool = 'bool'
    dict = 'dict'
    list = 'list'
    tuple = 'tuple'


def checkvalue(val):
    return type(val).__name__  # __type__


def config(key=None, val=None):
    global consoleconfig

    # 如果key为None或者key不存在,返回所有配置
    if(key == None or key not in consoleconfig):
        # return consoleconfig
        print(json.dumps(consoleconfig, indent=2, ensure_ascii=False))
        return False

    # 如果val是bool类型,设置值,否则返回key对应的val
    message = '\n'  # ()
    if type(val).__name__ == 'bool':
        message = message + LOGTYPE.配置.value % ('配置',)
        # print(key)
        # message = message + '【' + LOGTYPE[key].value % (key,)+'】'
        message = message + LOGTYPE.配置.value % ('【' + key+'】',)
        message = message + LOGTYPE.配置.value % ('开关',)
        message = message+':'+'开' if val == True else '关'
        # message = message + LOGTYPE.语句.value % ('开' if val == True else '关',)
        # console(LOGTYPE.配置.value % ('配置[%s]开关:%s' % (key, '开' if val == True else '关',),))
        if(val != consoleconfig[key]):
            print(message)
            consoleconfig[key] = val
        return True

    console('当前[%s]开关:%s' % (key, consoleconfig[key],), label=LOGTYPE.配置)
    return False


def console(*msg, ex=None, label=None, value=None, position=None):  # **args,
    global consoleconfig
    # 设置日志开关
    # print('------------------', type(label).__name__)
    labelname = label.name if type(label).__name__ == 'LOGTYPE' else label
    labelname = labelname if labelname != None else '无'
    labelvalue = label.value if type(label).__name__ == 'LOGTYPE' else None

    # print(labelname, labelvalue)

    if(labelname != None and value != None):
        config(labelname, value)

    op = ()

    # 输出异常
    if(ex):
        exfile = ex.__traceback__.tb_frame.f_globals["__file__"]
        exline = ex.__traceback__.tb_lineno
        message = '[%s:%s]' % (exfile, exline)
        op = op + (LOGTYPE.异常.value % (message,), )
        msg = msg+(str(ex),)

    # 输出位置
    # print('--------', position, consoleconfig['位置'],  position and consoleconfig['位置'])
    if(position and consoleconfig['位置']):
        op = op + (LOGTYPE.链接.value % (position,),)

    # 输出标签
    if(labelname != None and labelvalue != None):
        op = op + (labelvalue % (labelname,),)

    # print(consoleconfig[labelname], labelname)
    # print('----', 'labelname', labelname, 'labelvalue', labelvalue,  consoleconfig[labelname])

    # 根据配置决定是否输出日志
    if(consoleconfig[labelname] and len(msg) > 0):
        print(*(op + msg))
        return True
    return False


def consoleSet(*message, label=LOGTYPE.配置):
    console(*message, label=label)


def consoleReq(*message, label=LOGTYPE.请求):
    console(*message, label=label)


def consoleSql(*message, label=LOGTYPE.语句):
    console(*message, label=label)


def consoleErr(*message, label=LOGTYPE.异常):
    console(*message, label=label)

# -------------------------------
# 显示方式    |      效果
# -------------------------------
# 0           |     终端默认设置
# 1           |     高亮显示
# 4           |     使用下划线
# 5           |     闪烁
# 7           |     反白显示
# 8           |     不可见
# # -------------------------------
# -------------------------------------------
# 字体色     |       背景色     |      颜色描述
# -------------------------------------------
# 30        |        40       |       黑色
# 31        |        41       |       红色
# 32        |        42       |       绿色
# 33        |        43       |       黃色
# 34        |        44       |       蓝色
# 35        |        45       |       紫红色
# 36        |        46       |       青蓝色
# 37        |        47       |       白色
# -------------------------------------------


class zylog(unittest.TestCase):
    # def __init__(self, test):
    #     print('入口')

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

    # def testinit(self):
    #     print('入口')

    # def test_config(self):
    #     # colors = ['_黑_', '_红_', '_绿_', '_黄_', '_蓝_', '紫红', '青蓝', '_白_', '_白_', '_白_']
    #     # bgcolors = ['黑色文字', '红色文字', '绿色文字', '黄色文字', '蓝色文字', '紫红文字', ' 青蓝文字', '白色文字', '白色文字', '白色文字']
    #     # for color in range(30, 38):
    #     #     print('------------------------------------------------', bgcolors[color-30])
    #     #     for bgcolor in range(40, 48):
    #     #         aa = ()
    #     #         for showtype in range(10):  # range(10)
    #     #             # _color(, type=item2, color=item1),)
    #     #             text = str(showtype)+';'+str(color)+';'+str(bgcolor)+'m #' + \
    #     #                 colors[color-30] + '/' + colors[bgcolor-40]
    #     #             aa = aa + ('\033[%s;%s;%sm%s\033[0m' % (showtype, color, bgcolor, text),)
    #     #         print(*aa)

    #     # print(json.dumps(config(), indent=2, ensure_ascii=False))
    #     config()
    #     # # print(config('调试', True))
    #     # # print(config('调试'))
    #     # self.assertEqual(type(config('调试1')).__name__, 'dict')  # 返回指定标签的配置
    #     # # self.assertEqual(config('调试1', True), True)  # 设置指定标签的配置
    #     # self.assertEqual(config('调试'), False)  # 返回指定标签的配置
    #     # self.assertEqual(config('调试', True), True)  # 设置指定标签的配置

    def test_console(self):

        self.assertEqual(console('测试:test_query',  label=LOGTYPE.调试, value=True), True)
        self.assertEqual(console('测试:消息11', value=True), True)
        self.assertEqual(console('测试:语句日志', label=LOGTYPE.语句, value=True), True)
        self.assertEqual(console('测试:请求日志', label=LOGTYPE.请求, value=True), True)
        self.assertEqual(console('测试:设置通用的输出:开', value=True), True)
        self.assertEqual(console('测试:test_query',  label=LOGTYPE.调试), True)

        console('测试消息33', position='c:/0000/47python/zypylibs/zypylibs/function/zylog.py:224')
        console('测试消息44', label=LOGTYPE.请求, position='c:/0000/47python/zypylibs/zypylibs/function/zylog.py:225')
        try:
            raise Exception('测试异常')
        except Exception as ex:
            console(ex=ex)
            console('1111', ex=ex)

        # print(json.dumps(config(), indent=2, ensure_ascii=False))

    # def test_consoleSet(self):
    #     consoleSet(1, 2, 3)

    # def test_consoleReq(self):
    #     consoleReq(1, 2, 3)

    # def test_consoleSQL(self):
    #     consoleSql(1, 2, 3)

    # def test_consoleErr(self):
    #     consoleErr(1, 2, 3)


if __name__ == '__main__':
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()
