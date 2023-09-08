##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：147
# 执行时间：2023-01-07 22:09:12
##################################################
import unittest
from icecream import ic
import time
import uuid
import json
import sqlite3
from zypylibs.base.zyarr import mergearray
from zypylibs.base.zydict import mergedict
from zypylibs.function.zylog import console, consoleReq, consoleErr, consoleSql, LOGTYPE


def createfilter(data, prefix='where_', config=None):
    sqlwhere = []  # and (flag!=\'删除\' or flag is null)'
    sqlparams = ()

    ic(data)
    for k, v in data.items():
        # ic(k, v)

        prefixs = k.split('_')
        if(len(prefixs) != 2):
            continue

        how = prefixs[0]
        key = prefixs[1]
        # if(k.startswith(prefix)):
        #     key = k.replace(prefix, '')
        ic(key, config)
        if(config is not None):
            if (key not in config):
                # ic(key, config)
                continue

        ic(how, key)

        mapping = {'where': ' = ',  'eq': ' = ', 'ne': ' != ', 'gt': ' > ', 'lt': ' < ', 'ge': ' >= ', 'le': ' <= ', 'like': ' like '}
        if(how in mapping):

            ic(how, mapping[how])
            if v == '':
                if how == 'where':
                    sqlwhere.append(' and (' + key + ' = ? or ' + key + ' is null)')  #
                    sqlparams = sqlparams + (v,)
            else:
                sqlwhere.append(' and ' + key + mapping[how] + '?')
                sqlparams = sqlparams + (v,)
        # if(how == 'like'):
        #     if v == '':
        #         sqlwhere.append(' and (' + key + ' like ? or ' + key + ' is null)')
        #     else:
        #         sqlwhere.append(' and ' + key + ' like ?')
        if(how == 'update'):
            sqlwhere.append(key + '=?')
            sqlparams = sqlparams + (v,)

    sqlwhere = ''.join(sqlwhere)
    # if(prefix == 'where_'):

    # if(prefix == 'update_'):
    #     sqlwhere = ','.join(sqlwhere)
    # if(prefix == 'like_'):
    #     sqlwhere = ''.join(sqlwhere)
    # ic('####createfilter', sqlwhere, sqlparams)
    return {'sqlwhere': sqlwhere, 'sqlparams': sqlparams}


class zysql(unittest.TestCase):
    # def __init__(self, test):
    #     ic('入口')
    def setUp(self) -> None:
        # ic('构建')
        console(label=LOGTYPE.无, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:460')
        console(label=LOGTYPE.调试, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:461')
        console(label=LOGTYPE.链接, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:462')
        console(label=LOGTYPE.配置, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:463')
        console(label=LOGTYPE.请求, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:464')
        console(label=LOGTYPE.语句, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:465')
        console(label=LOGTYPE.异常, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:466')
        return super().setUp()

    def tearDown(self) -> None:
        # ic('销毁')
        return super().tearDown()

    def test_createfilter(self):
        result = createfilter({
            'tbname': 'tb0112',
            'where_表单编辑': '1',
            'like_AA': 1111,
        })
        ic(result)
        # self.assertEqual(result, {'sqlwhere': ' and 表单编辑=? and AA like ?', 'sqlparams': ('1',)})  # 使用数组作为参数  # 可以
        self.assertEqual(result, {'sqlwhere': ' and 表单编辑=? and AA like ?', 'sqlparams': ('1', 1111)})  # 使用数组作为参数  # 可以


if __name__ == '__main__':
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()
