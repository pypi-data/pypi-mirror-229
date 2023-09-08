##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：0
# 执行时间：2023-01-07 22:09:12
##################################################
# from zypylibs.function.zycommon import updatedescribe
# updatedescribe(__file__)


import os
import json
import chardet
import unittest
import shutil
import qrcode
from zypylibs.base.zystr import cut_text
from zypylibs.base.zybyte import tostr, tobyte


def getenv(file=__file__):
    names1 = os.path.split(file)

    names2 = os.path.splitext(names1[1])

    # print(names1[0], names2[0], names2[1])

    return (names1[0], names2[0], names2[1])


def checkdir(exportpath, isdelete=False, iscreate=True):

    if os.path.exists(exportpath) and isdelete:
        shutil.rmtree(exportpath)
    if not os.path.exists(exportpath):
        if iscreate:
            os.makedirs(exportpath)
            return True
        else:
            return False
    else:
        return True
# ↑ 检查目录


def readfile(path='a.txt', encoding='utf-8'):

    with open(path, 'r', encoding=encoding) as f:
        data = f.read()
        return data
# ↑ 读取文件


def readfileauto(path, isline=False, isinfo=False):
    """猜测文件编码并读取文件内容

    Args:
        path (_type_): 文件路径
        isline (bool, optional): 是否按行读取. Defaults to False.
        isinfo (bool, optional): 是否返回编码. Defaults to False.

    Returns:
        _type_: 文件内容,文本类型
        如果isline为True,则是数组类型
        如果isinfo为True,则是字典类型
        content:文件内容,也看isline配置
        filecode:解析编码
        filecode2:修正编码
    """
    content = ''
    filecode = ''
    try:
        with open(path, 'rb') as f:
            filedata = f.read()
            dicts = chardet.detect(filedata)
            filecode = dicts['encoding']
    except Exception as ex:
        return {'content': '', 'errorsmg': str(ex)}

    filecode2 = filecode
    if(filecode2 == 'Windows-1254'):
        filecode2 = 'utf-8'

    if(filecode2 == 'GB2312'):
        filecode2 = 'gbk'
    try:
        with open(path, 'r', encoding=filecode2) as file1:
            if(isline):
                content = file1.readlines()
            else:
                content = file1.read()
    except Exception as ex:
        print(filecode2+'|'+str(ex))
    if(isinfo):
        return {'content': content, 'filecode': filecode, 'filecode2': filecode2}
    return content
# ↑ 自动读取文件


def readfilebyte(path, cb):

    f = open(path, 'rb')
    size = os.path.getsize(path)
    # 读取文件
    filebyte = []
    tempidx = 0
    while True:
        data = f.read(1)
        # print(data)
        filebyte.append(cb(data))
        tempidx += 1
        if tempidx >= size:
            break
    f.close()
    return filebyte
# ↑ 字节读取文件


def readfilelist(path):
    datalist = []
    index = 0
    for (root, dirs, files) in os.walk(path):
        for item in dirs:
            index = index+1
            fullpath = os.path.join(root, item)
            datalist.append({'index': index, 'filepath': root, 'filename': item, 'filetype': 'D', 'fullpath': fullpath})
        for item in files:
            index = index+1
            fullpath = os.path.join(root, item)
            fileinfo = os.path.basename(fullpath)
            filename, filesuffix = os.path.splitext(fileinfo)
            datalist.append({'index': index, 'filepath': root, 'filename': filename, 'filetype': 'F', 'filesuffix': filesuffix, 'fullpath': fullpath})
    return datalist
# ↑ 读取文件清单


def writefile(path, content, type='w', encoding='utf-8'):
    with open(path, type, encoding=encoding) as f:
        f.write(content)
# ↑ 写入文件


def writeFilebyte(filearr, path):
    f = open(path, 'w')
    for file in filearr:
        f.write(file)
    f.close()
# ↑ 写入文件字节.这个跟上面的原来重名了


def getextname(name, type=1):
    """获取文件名

    Args:
        name (_type_): _description_

    Returns:
        _type_: 文件
    """
    ext1 = name.split(".")[-1]
    ext2 = os.path.splitext(name)[-1]
    if(type == 1):
        return ext1
    if(type == 2):
        return ext2
# ↑ 获取扩展名


def getfilename(name):
    """获取文件名

    Args:
        name (_type_): _description_

    Returns:
        _type_: 文件
    """
    name = getfullname(name)
    return os.path.splitext(name)[0]
# ↑ 获取文件名


def getfullname(name):
    """获取完整文件名(文件名+扩展名)

    Args:
        name (_type_): _description_

    Returns:
        _type_: _description_
    """
    return os.path.basename(name)
# ↑ 获取文件名+扩展名)


def getfilepath(name):
    """获取文件路径

    Args:
        name (_type_): _description_

    Returns:
        _type_: _description_
    """
    return os.path.dirname(name)
# ↑读取文件清单


def getfullpath(name):
    """_summary_

    Args:
        name (_type_): _description_

    Returns:
        _type_: _description_
    """
    return os.path.basename(name)
# ↑读取文件清单


def getfiles(dbroot=r'C:\0000\54sqlite\bak'):
    ls = []
    for dbname in os.listdir(dbroot):
        if(dbname.endswith('.db')):
            dbpath = os.path.join(dbroot, dbname)
            ls.append(dbpath)
    print(json.dumps(ls, indent=2, ensure_ascii=False))
    return ls


def getfiles2(fileroot=r'H:\20221213', filelevel=1, before=None, complete=None):
    """读取文件列表清单

    Args:
        fileroot (regexp, optional): 要搜索的根目录. Defaults to r'H:\20221213'.
        before (_type_, optional): 获取信息前分析,主要判断目录名决定是否继续下探. Defaults to None.
        complete (_type_, optional): 获取信息后分析,主要处理信息内容或者是否加入到清单中. Defaults to None.

    Returns:
        _type_: _description_
    """
    ls = []

    for fileitem in os.listdir(fileroot):
        fullpath = os.path.join(fileroot, fileitem)
        filetype = 'D' if os.path.isdir(fullpath) else 'F'
        fileinfo = {
            'fileroot': fileroot,  # 上级目录
            'fileitem': fileitem,
            'fullpath': fullpath,
            'filepath': os.path.dirname(fullpath),
            'filetype': filetype,
            'filelevel': filelevel
        }

        if(before is not None):
            fileinfo = before(fileinfo)
        if(fileinfo is None or fileinfo is False):
            continue

        if(filetype == 'D'):
            ls = ls + getfiles2(fullpath, filelevel+1, before, complete)

        if(filetype == 'F'):
            fullname = os.path.basename(fullpath)
            fileinfo['fullname'] = fullname
            fileinfo['filename'] = os.path.splitext(fullname)[0]
            fileinfo['filesuffix'] = os.path.splitext(fullname)[1]

        if(complete is not None):
            fileinfo = complete(fileinfo)
        if(fileinfo is None or fileinfo is False):
            continue
        ls.append(fileinfo)

    return ls


def filetostr(path, exportpath=None, cutlen=2300, iszip=False):
    # 文件转换为字符串  #不能超过2400长度,使用2300分出来37个文件
    filecodestr = ''.join(readfilebyte(path, lambda m: tostr(m)))
    # 压缩字符串  #不能超过800长度,使用750分出来38个文件
    if(iszip):
        filecodestr = ''.join(list(map(lambda m: chr(int(str(m), 16) + 19968), cut_text(filecodestr, 3))))

    # 生成图片
    if(exportpath is not None):
        filecodearr = cut_text(filecodestr, cutlen)
        for idx, filecode in enumerate(filecodearr):
            qrcode.make(filecode).save(exportpath+'二维码'+str((idx+1)).zfill(2)+'.png')
        # return len(filecodearr)
    
    return filecodestr


def strtofile(filetext, exportpath, iszip=False):
    if(iszip):
        filetext = ''.join(list(map(lambda m:  str((hex(ord(m) - 19968)).replace('0x', '')).rjust(3, '0'),  cut_text(filetext, 1))))
    aa = list(map(lambda m: tobyte(m),  cut_text(filetext, 2)))
    f = open(exportpath, 'wb')
    for item in aa:
        f.write(item)
    f.close()


class zyfile(unittest.TestCase):
    testfile = r'C:\0000\47python\zypylibs\README.md'
    exportpath = os.getcwd()+'/imgs/code1/'

    def test_getenv(self):
        self.assertEqual(getenv(__file__), ('c:/0000/47python/zypylibs/zypylibs/function', 'zyfile', '.py'))

    def test_checkdir(self):
        self.assertEqual(checkdir(self.exportpath), True)

    def test_getextname(self):
        self.assertEqual(getextname(self.testfile, type=1), 'md')
        self.assertEqual(getextname(self.testfile, type=2), '.md')

    def test_readfile(self):
        self.assertEqual(readfile(r'C:\0000\47python\template\入口.txt'), 'if __name__ == \'__main__\':')

    def test_readfileauto(self):
        self.assertEqual(readfileauto(r'C:\0000\47python\template\入口.txt'), 'if __name__ == \'__main__\':')

    def test_readfilebyte(self):
        self.assertEqual(readfilebyte(r'C:\0000\47python\template\入口.txt', lambda m: tostr(m)), [
                         '69', '66', '20', '5f', '5f', '6e', '61', '6d', '65', '5f', '5f', '20', '3d', '3d', '20', '27', '5f', '5f', '6d', '61', '69', '6e', '5f', '5f', '27', '3a'])

    def test_getfilename(self):
        self.assertEqual(getfilename(self.testfile), 'README')

    def test_getfullname(self):
        self.assertEqual(getfullname(self.testfile), 'README.md')

    def test_getfilepath(self):
        self.assertEqual(getfilepath(self.testfile), 'C:\\0000\\47python\\zypylibs')
        self.assertEqual(getfilepath('/laydate/need/laydate.css'), '/laydate/need')

    def test_filetostr(self):
        result1 = filetostr(r'C:\0000\47python\zypylibs\imgs\A.png', exportpath=r'C:\0000\47python\zypylibs\imgs\A\\')  # ,
        self.assertGreater(len(result1), 0)
        result2 = filetostr(r'C:\0000\47python\zypylibs\imgs\A.png', iszip=True)
        self.assertGreater(len(result2), 0)

        writeFilebyte(result1, r'C:\0000\47python\zypylibs\imgs\AA.txt')
        writeFilebyte(result2, r'C:\0000\47python\zypylibs\imgs\BB.txt')

    def test_strtofile(self):
        result1 = strtofile(readfile(r'C:\0000\47python\zypylibs\imgs\AA.txt'),
                            exportpath=r'C:\0000\47python\zypylibs\imgs\AA.png')
        # self.assertEqual(len(result1), 84094)
        result2 = strtofile(readfileauto(r'C:\0000\47python\zypylibs\imgs\BB.txt'),
                            exportpath=r'C:\0000\47python\zypylibs\imgs\BB.png', iszip=True)
        # self.assertEqual(len(result2), 28032)
        # writeFilebyte(result1, r'C:\0000\47python\zypylibs\imgs\AA.txt')
        # writeFilebyte(result2, r'C:\0000\47python\zypylibs\imgs\BB.txt')

    # def test_getfiles(self):
    #     self.assertEqual(getfiles(r'C:\0000\47python\template'), [
    #         r'C:\0000\47python\template\入口.txt',
    #         r'C:\0000\47python\template\注释.txt',
    #     ])

    # def test_getfilename1(self):
    #     self.assertEqual(getfilename1(self.testfile), 'README')

    def test_tostr(self):
        self.assertEqual(1, 1)

    def test_tostr1(self):
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
