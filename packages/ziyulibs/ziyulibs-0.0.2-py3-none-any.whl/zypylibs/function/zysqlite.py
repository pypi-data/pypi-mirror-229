##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：147
# 执行时间：2023-01-07 22:09:12
##################################################
import unittest
# from icecream import ic
import time
import uuid
import json
import sqlite3
from zypylibs.base.zyarr import mergearray
from zypylibs.base.zydict import mergedict
from zypylibs.function.zylog import console, consoleReq, consoleErr, consoleSql, LOGTYPE
# from zypylibs.function.zycommon import updatecomment, updatedescribe


def droptb(dbname, tbname):
    execute(dbname, 'drop table if exists %s' % (tbname,))

# 清理数据


def erasetb(dbname, tbname):
    execute(dbname,  'delete * from %s' % (tbname,))


def createparams(data, fields, type=1, defval=''):
    """创建参数
    1.数组/元组:从对象中提取配置字段中的所有数据并组装
    2.字典:主要用于解决对象中有的字段不存在值的情况

    Args:
        data (_type_): 数据源对象
        fields (_type_): 字段配置集合
        type (int, optional): 返回类型. Defaults to 1.
        defval (_type_): 默认值
    Returns:
        _type_: 根据传入的type,1:返回数组,2:返回元组,3返回字典
    """
    if (type == 1):
        return list(map(lambda x: str(data[x]) if x in data else defval, fields))
    if (type == 2):
        return tuple(map(lambda x: str(data[x]) if x in data else defval, fields))
    if (type == 3):
        dc = {}
        for x in fields:
            dc[x] = str(data[x]) if x in data else defval
        return dc

# 用于解决值为None而产生的错误 20220428


def createparams1(data, fields, type=1):
    # print(data,fields)
    if (type == 1):
        return list(map(lambda x: (data[x] if data[x] != None else '') if x in data else '', fields))
    if (type == 2):
        return tuple(map(lambda x: (data[x] if data[x] != None else '') if x in data else '', fields))


def createdb(dbname, tbname, fields, isAddSys=True):
    """创建表

    Args:
        dbname (_type_): 数据库地址
        tbname (_type_): 数据表名称
        fields (_type_): 字段配置集合
        isAddSys (bool, optional): 是否添加系统字段(如aid,gid等). Defaults to True.
    """
    # 表名,主键
    fieldarr = []
    if type(fields) == list:
        for field in fields:
            fieldarr.append(field + ' TEXT')
    #
    if type(fields) == dict:
        for key, value in fields.items():
            if value not in ['TEXT', 'INTEGER', 'DATETIME']:
                consoleErr('不支持类型:' + value + ',字段:' + key)
                continue
            fieldarr.append(key + ' ' + value)

    # 添加备注
    if (isAddSys):
        fieldarr.append('aid TEXT')  # 自动uuid,用于合并数据时判断是否为同一条记录
        fieldarr.append('gid TEXT')  # 自动uuid,用于删除数据时判断是否为同一条记录
        # fieldarr.append( 'pid TEXT') #父id,备用
        # fieldarr.append( 'gid TEXT') #自动uuid
        fieldarr.append('flag TEXT')  # 标识 0,在用,1删除
        fieldarr.append('remark TEXT')
        fieldarr.append('createuser INTEGER')
        fieldarr.append('createtime DATE')
        fieldarr.append('updateuser INTEGER')
        fieldarr.append('updatetime DATE')
        fieldarr.append('deleteuser INTEGER')
        fieldarr.append('deletetime DATE')
    sqlstr = 'CREATE TABLE IF NOT EXISTS %(tbname)s (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,%(fieldstr)s)' % {
        'tbname': tbname, 'fieldstr': ','.join(fieldarr)}
    return execute(dbname, sqlstr)


def _dict_factory(cursor, row):
    """查询使用

    Args:
        cursor (_type_): 游标,可以获取查询的信息
        row (_type_): 行记录

    Returns:
        _type_: 返回字典
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def query(dbname, sqlstr, params=None, type=1):
    """查询语句

    Args:
        dbname (_type_): 数据库地址
        sqlstr (_type_): _description_
        params (_type_, optional): _description_. Defaults to None.
        type (int, optional): _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """
    try:
        conn = sqlite3.connect(dbname)
        conn.row_factory = _dict_factory
        cursor = conn.cursor()
        consoleSql('query', sqlstr, params)
        if (params == None):
            cursor.execute(sqlstr)
        else:
            cursor.execute(sqlstr, params)

        if (type == 2):
            return {
                'datalist': cursor.fetchall(),
                'description': cursor.description
            }
        return cursor.fetchall()
    finally:
        if conn:
            conn.close()


def _querydb_where(item, params, index):
    """_summary_

    Args:
        item (_type_): _description_
        params (_type_): _description_
        index (_type_): _description_

    Returns:
        _type_: _description_
    """

    paramstype = type(params).__name__  # 获取参数的类型, 如果是集合或者元组,就用?,如果是字典,就要使用":字段名"
    fieldinfo = item.split('|')
    tablefield = fieldinfo[0] if (len(fieldinfo) >= 1) else ''  # 表对应的字段
    valuefield = fieldinfo[1] if (len(fieldinfo) >= 2) else ''  # 值对应的字段
    conditionstr = fieldinfo[2] if (len(fieldinfo) >= 3) else '='  # 拼接条件

    if (len(tablefield) > 0 and conditionstr in ['=', '!=', '>', '>=', '<', '<=', 'like', 'is', 'is not']):
        if paramstype == 'dict':
            if valuefield == '':
                return {
                    'sqlwhere': tablefield,
                    'sqlparams':  {},
                }
            else:
                return {
                    'sqlwhere': tablefield + ' ' + conditionstr + ' ' + (':' + valuefield if valuefield != 'None' else 'null'),
                    'sqlparams': {valuefield: params[valuefield]},
                }
        if paramstype == 'list':
            if valuefield == '':
                return {
                    'sqlwhere': tablefield,
                    'sqlparams':  [],
                }
            else:
                return {
                    'sqlwhere': tablefield + ' ' + conditionstr + ' ' + '?',
                    'sqlparams':  [params[index-1]],
                }
        if paramstype == 'tuple':
            if valuefield == '':
                return {
                    'sqlwhere': tablefield,
                    'sqlparams':  [],
                }
            else:
                return {
                    'sqlwhere': tablefield + ' ' + conditionstr + ' ' + '?',
                    'sqlparams': [list(params)[index-1]],
                }

    # in和not in需要知道参数的长度,所以要先取到参数值,这里dict和集合的方式不一样
    # 这两个的参数必须是数组或者元组
    if (len(tablefield) > 0 and conditionstr in ['in', 'not in']):
        value = []  # 得到的结果必须是个数组
        if paramstype == 'dict':
            value = list(params[valuefield])
            return {
                'sqlwhere': tablefield + ' ' + conditionstr + '(' + ','.join(list(map(lambda m: ':' + valuefield + str(m + 1), range(len(value))))) + ')',
                # [{valuefield: params[valuefield]}],  # value,

                'sqlparams': mergedict(list(map(lambda m: {valuefield + str(m + 1): value[m]}, range(len(value)))))
            }
        if paramstype == 'list':
            value = list(params[index-1])
            return {
                'sqlwhere': tablefield + ' ' + conditionstr + '(' + ','.join('?' * len(value)) + ')',
                'sqlparams': value,
            }
        if paramstype == 'tuple':
            value = list(list(params)[index-1])  # 如果参数是元组, 就要先转成数组再按照索引取值, 再把里面的值转成数组
            return {
                'sqlwhere': tablefield + ' ' + conditionstr + '(' + ','.join('?' * len(value)) + ')',
                'sqlparams': value,
            }


def querydb(dbname, tbname, fields=[],  params=None, returntype=1, showfields='*', orderfields=[], ):
    """查询数据表

    Args:
        dbname (_type_): 数据库地址
        tbname (_type_): 数据表名称
        fields (list, optional): _description_. Defaults to [].
        params (_type_, optional): _description_. Defaults to None.
        returntype (int, optional): _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """
    if (type(showfields).__name__ == 'list'):
        showfields = '.'.join()

    sqlstr = 'select %s from %s ' % (showfields, tbname)
    sqlarr = []
    sqlparams = []
    index = 0  # 记录参数的索引,统计个数
    paramstype = type(params).__name__  # 获取参数的类型, 如果是集合或者元组,就用?,如果是字典,就要使用":字段名"
    for index1, item in enumerate(fields):
        fieldtype = type(item).__name__  # 获取字段配置类型,如果是字符串就是第一层,用and连接,如果是数组就是第二层,用or连接
        # print(fieldtype)
        if fieldtype == 'str':
            index = index + 1
            sqlarr.append(_querydb_where(item, params, index))
        if fieldtype == 'list':
            sqlarr2 = list(map(lambda m, i: _querydb_where(m, params, index + i), item, range(len(item))))
            index += len(item)
            sqlwhere2 = list(map(lambda m: m['sqlwhere'], sqlarr2))
            sqlparams2 = list(map(lambda m: m['sqlparams'], sqlarr2))

            # 合并返回的字典集合为一个集合,或者合并数组集合为一个数组
            sqlparams2 = mergedict(sqlparams2) if paramstype == 'dict' else mergearray(sqlparams2)
            sqlarr.append({
                'sqlwhere': '(' + ' or '.join(sqlwhere2) + ')',
                'sqlparams': sqlparams2
            })

    if len(sqlarr) > 0:
        # print(sqlarr)
        sqlwhere = list(map(lambda m: m['sqlwhere'], sqlarr))
        sqlparams = list(map(lambda m: m['sqlparams'], sqlarr))
        sqlstr = sqlstr + ' where ' + (' and '.join(sqlwhere))
        sqlparams = mergedict(sqlparams) if paramstype == 'dict' else mergearray(sqlparams)

    return query(dbname, sqlstr, sqlparams, returntype)


def execute(dbname, sqlstr, params=None, returntype=1):
    """执行语句

    Args:
        dbname (_type_): 数据库地址
        sqlstr (_type_): _description_
        params (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    try:
        conn = sqlite3.connect(dbname)
        if (params == None):
            cursor = conn.execute(sqlstr)
        else:
            consoleSql(sqlstr, params)
            if isinstance(params, tuple) or isinstance(params, dict):
                cursor = conn.execute(sqlstr, params)
            if isinstance(params, list):
                cursor = conn.executemany(sqlstr, params)
        conn.commit()
        if (returntype == 2):
            return cursor.lastrowid
        if (returntype == 9):
            return cursor
        return cursor.rowcount
    finally:
        if conn:
            conn.close()

# 逐条执行

# 可以使用insertdb1替代,参考demo2002\2020022301Hsp\demo20200611喜马拉雅2.py
# def insertdb(dbname, tbname, fields, datalist, operuser='admin'):
#     conn = sqlite3.connect(dbname)
#     sqlstr = ''
#     try:
#         # 表名,主键
#         fieldlist = []
#         valuelist = []
#         #
#         fieldlist.append('aid')
#         valuelist.append('uuid.uuid')
#         fieldlist.append('gid')
#         # fieldlist.append('flag') #标识 0,在用,1删除
#         # fieldlist.append('remark')
#         fieldlist.append('createuser')
#         fieldlist.append('createtime')
#         # fields=
#         if type(fields).__name__ == 'list':
#             for idx, field in enumerate(fields):
#                 fieldlist.append('%s' % (field))
#                 valuelist.append('{%s}' % (field))
#         #
#         if type(fields).__name__ == 'dict':
#             for key, value in fields.items():
#                 fieldlist.append('%s' % (key))
#                 valuelist.append('{%s}' % (value))

#         # fieldlist.append('batch')
#         # fieldlist.append(uuid.uuid1())

#         # 添加备注
#         # fieldlist.append('remark')
#         # valuelist.append('%s' % (remark))
#         # 添加日期
#         fieldlist.append('createtime')
#         valuelist.append(
#             '%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
#         )
#         sqlstr = ' insert into %s(%s) values(%s)' % (
#             tbname,
#             ','.join(fieldlist),
#             ','.join(valuelist),
#         )
#         # console(sqlstr, list, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:341')

#         # def change(value):
#         #     if int(value.group()) < 5:
#         #         return '0'
#         #     else:
#         #         return '0'

#         for index, params in enumerate(datalist):
#             # execsql = sqlstr.format(**params)
#             # conn.execute(execsql)
#             # execsql = re.sub(r'\'\{[\w\s<>\/]+ \}\'', '?', sqlstr)
#             # conn.execute(execsql, getdata(params, fields))
#             execsql = re.sub(r'\'(\{)([\w\s<>\/]+ )(\})\'', ':\\2', sqlstr)
#             # 20220930 这里好奇怪,为什么要在上面拼接为"{字段名}"的结构然后在这里替换呢?
#             console(execsql, params, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:356')
#             conn.execute(execsql, params)
#         cursor = conn.commit()
#         # return cursor.rowcount
#     except Exception as ex:
#         console(ex, 'insertdb报错', sqlstr, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:361')
#         return False
#     finally:
#         conn.close()


# 批量执行
# datalist： 可以是字典集合，也可以是数组/元祖集合 ,如果是字典类型需要传入values
# fields :表中的字段名
# values :对应程序中的属性名 ,用于取字典类型的数据
# 有好几种思路
# 1. 执行语句时还是用?结构,只是把字典转成需要的数组,并拼接系统字段
# 2. 如果是字典类型,可以使用":字段"的结构来拼接,但是需要考虑字典中没有该值的情况,并且需要update系统字段


# 又感觉这样做其实没有意义,因为集合中的类型一般都是一致的, 不应该在循环里判断
def insertdb1(dbname, tbname, fields, datalist, operuser='admin', values=None, paramscb=None):
    """执行数据表
    会根据配置的字段自动生成插入语句

    Args:
        dbname (_type_): 数据库地址
        tbname (_type_): 数据表名称
        fields (_type_): 字段配置集合
        datalist (_type_): _description_
        operuser (str, optional): 执行人员. Defaults to 'admin'.
        values (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    fieldlist = json.loads(json.dumps(fields))
    fieldlist = fieldlist + ['aid', 'gid', 'createuser', 'createtime']
    valuelist = []

    paramslist = []
    gid = str(uuid.uuid1())
    for index, item in enumerate(datalist):
        paramsitem = []
        # 如果是集合类型,添加系统字段
        if type(item).__name__ in ['list', 'tuple']:
            valuelist = list(map(lambda m: '?', fieldlist))
            if len(fields) != len(item):
                raise (sqlstr)('第%s条参数不匹配,字段%s,数据%s' % (index, len(fields), len(item)))

            paramsitem = list(item) + [str(uuid.uuid1()), str(uuid.uuid1()), operuser,
                                       time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())]

        # 如果是字典类型 , 取字典的keys为fields
        if type(item).__name__ == 'dict':
            valuelist = list(map(lambda m: ':'+m, fieldlist))
            # paramsitem = createparams(item, list(item.keys()), type=1)
            paramsitem = mergedict([{
                'aid': str(uuid.uuid1()),
                'gid': gid,
                'createuser': operuser,
                'createtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            }, item])
            if (paramscb != None):
                paramsitem = paramscb(paramsitem)
        paramslist.append(paramsitem)
    # 直接判断values, 如果不为None就按照字典处理, 否则按照数组/元组处理
    # paramslist = list(map(
    #     lambda x: list(x) + [
    #         str(uuid.uuid1()),
    #         str(uuid.uuid1()),
    #         operuser,
    #         time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    #     ], datalist)) if values is None else list(map(
    #         # list(fields.values())
    #         lambda x: createparams(x, values,  type=1) + [
    #             str(uuid.uuid1()),
    #             str(uuid.uuid1()),
    #             operuser,
    #             time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    #         ],
    #         datalist))

    # paramslist = list(map(
    #     lambda x: (list(x) if values is None else createparams(x, values,  type=1)) + [
    #         str(uuid.uuid1()),
    #         str(uuid.uuid1()),
    #         operuser,
    #         time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    #     ], datalist))

    sqlstr = ' insert into %s(%s) values(%s)' % (
        tbname,
        ','.join(fieldlist),
        ','.join(valuelist),
    )
    # consoleSql(sqlstr, paramslist)
    return execute(dbname, sqlstr, paramslist)


def executelist(db, tb, title1, content1):
    result = createdb(db, tb, title1)
    # print('创建表名:\r\n',result)
    result = createsql(tb, title1, type=1)
    # print('创建语句:\r\n',result)

    content1 = list(map(lambda x: createparams(x, title1), content1))
    # print(content1)
    result = execute(db, result, content1)
    # print(result)
    return result


# 1234:增删改查
def createsql(tbname, fields=[], pk='id', type=4):
    sql = ''
    # 增加
    if (type == 1):
        fields1 = ','.join(map(lambda x: x, fields))
        # fields2=','.join(map(lambda x:"%("+x +")s",fields))
        fields2 = ','.join(map(lambda x: '?', fields))
        sql = 'insert into %(tbname)s(%(fields1)s) values(%(fields2)s)' % ({'tbname': tbname, 'fields1': fields1, 'fields2': fields2})
    # 导入
    if (type == 11):
        fields1 = ','.join(map(lambda x: x, fields))
        # fields2=','.join(map(lambda x:"%("+x +")s",fields))
        fields2 = ','.join(map(lambda x: '?', fields))
        sql = 'insert into %(tbname)s(%(fields1)s,importtime) values(%(fields2)s,\'%(importtime)s\')' % (
            {'tbname': tbname, 'fields1': fields1, 'fields2': fields2, 'importtime': time.strftime('%Y-%m-%d %H:%M:%S')})

    # 删除
    if (type == 2):
        if (pk == ''):
            sql = 'delete from %(tbname)s' % ({'tbname': tbname})
        else:
            sql = 'delete from %(tbname)s where %(pk)s=?' % ({'tbname': tbname, 'pk': pk})
    # 修改
    if (type == 3):
        fields1 = ','.join(map(lambda x: x + '=?', fields))
        sql = 'update %(tbname)s set %(fields1)s where %(pk)s=?' % ({'tbname': tbname, 'fields1': fields1, 'pk': pk})

    # 想增加一种写法 ,使用
    if (type == 33):
        fields1 = ','.join(map(lambda x: x + '=:' + x, fields))
        sql = 'update %(tbname)s set %(fields1)s where %(pk)s=:%(pk)s' % ({'tbname': tbname, 'fields1': fields1, 'pk': pk})

    # 查询
    if (type == 4):
        fields1 = ','.join(map(lambda x: x, fields))
        # sql='select {} from {}'.format(fields1,tbname)
        if (len(fields) == 0):
            sql = 'select * from %s' % (tbname)
        else:
            sql = 'select %s from %s' % (fields1, tbname)

    if (type == 5):
        # print(fields)
        fields1 = ' and '.join(map(lambda x: x+'=?', fields))
        # print(fields1)
        sql = ' where %s' % (fields1)
    return sql


class zysqlite(unittest.TestCase):
    # def __init__(self, test):
    #     print('入口')
    def setUp(self) -> None:
        # print('构建')
        console(label=LOGTYPE.无, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:460')
        console(label=LOGTYPE.调试, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:461')
        console(label=LOGTYPE.链接, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:462')
        console(label=LOGTYPE.配置, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:463')
        console(label=LOGTYPE.请求, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:464')
        console(label=LOGTYPE.语句, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:465')
        console(label=LOGTYPE.异常, value=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:466')
        return super().setUp()

    def tearDown(self) -> None:
        # print('销毁')
        return super().tearDown()

    # def test_query(self):
    #     self.assertEqual(len(query('C:/0000/47python/zypyweb/db2207.db', 'select * from tb0712 where flag in (99)')), 0)  # 可以
    #     self.assertEqual(len(query('C:/0000/47python/zypyweb/db2207.db', 'select * from tb0712 where flag in (?)', ('99',))), 0)  # 用一个参数接收  # 不可
    #     self.assertEqual(len(query('C:/0000/47python/zypyweb/db2207.db', 'select * from tb0712 where flag in (?,?)', (99, 99))), 0)   # 使用元组作为参数  # 可以
    #     self.assertEqual(len(query('C:/0000/47python/zypyweb/db2207.db', 'select * from tb0712 where flag in (?,?)', [99, 99])), 0)  # 使用数组作为参数  # 可以

    # def test_querydb(self):
    #    # console(isprintdebug=True, position='c:/0000/47python/zypylibs/zypylibs/function/zysqlite.py:480')
    #     # 测试in语句
    #     ls = querydb('C:/0000/47python/zypyweb/db2207.db', 'tb0712', [
    #         'flag|flag|in',
    #         ['备用字段4|备用字段41', '备用字段4|备用字段42']
    #     ], {
    #         'flag': (1, 2),
    #         '经度坐标': 113.224411,
    #         '纬度坐标': 22.687409,
    #         '备用字段41': 10,
    #         '备用字段42': '11'  # 要用数字类型?
    #     })
    #     self.assertEqual(len(ls), 0)  # 可以
    #     # # 测试in语句,测试参数是数组和元组
    #     ls = querydb('C:/0000/47python/zypyweb/db2207.db', 'tb0712', [
    #         'flag|flag|in',
    #         '备用字段4|备用字段4'
    #     ], [
    #         [1, 2],
    #         10
    #     ])
    #     self.assertEqual(len(ls), 0)  # 可以
    #     ls = querydb('C:/0000/47python/zypyweb/db2207.db', 'tb0712', [
    #         'flag|flag|in',
    #         '备用字段4|备用字段4'
    #     ], (
    #         (1, 2),
    #         10
    #     ))
    #     self.assertEqual(len(ls), 0)  # 可以

    #     # 测试只有一个
    #     ls = querydb('C:/0000/47python/zypyweb/db2207.db', 'tb0712', [
    #         '导入源|导入源'
    #     ], [
    #         'db20220930'
    #     ])
    #     print(len(ls))
    #     self.assertEqual(len(ls), 5698)  # 可以
    #     # 测试
    #     ls = querydb('C:/0000/47python/zypyweb/db2207.db', 'tb0712', [
    #         'flag|flag|in'
    #     ], ((1, 2),))
    #     self.assertEqual(len(ls), 64)  # 可以

    # def test_execute(self):
    #     print(execute('C:/0000/47python/zypyweb/db2207.db', 'insert into test1(A) values(?)', (11111,), returntype=2))  # 可以 ,这里需要增加验证 ?类型不能是字典,只能是数组或者元组
    #     print(execute('C:/0000/47python/zypyweb/db2207.db', 'insert into test1(A) values(?)',
    #           [(22222,)], returntype=2))  # 可以 ,这里需要增加验证 ?类型不能是字典,只能是数组或者元组
    #     print(execute('C:/0000/47python/zypyweb/db2207.db', 'insert into test1(A) values(?)',
    #           [(33333,), (44444,)], returntype=2))  # 可以 ,这里需要增加验证 ?类型不能是字典,只能是数组或者元组
    #     self.assertEqual(execute('C:/0000/47python/zypyweb/db2207.db', 'delete from test1 where A=:A',
    #                      {'A': '1'}), 1)  # 可以 ,这里需要增加验证 ?类型不能是字典,只能是数组或者元组
    #     self.assertEqual(execute('C:/0000/47python/zypyweb/db2207.db', 'delete from test1 where A=?', ('3',)), 1)  # 可以
    #     self.assertEqual(execute('C:/0000/47python/zypyweb/db2207.db', 'delete from test1 where A=?', ['5']), 1)  # 可以
    #     print(execute('C:/0000/47python/zypyweb/db2207.db', 'update test1 set A=? where length(A)=5', (None,), returntype=2))  # 可以 ,这里需要增加验证 ?类型不能是字典,只能是数组或者元组

    # def test_createdb(self):
    #     self.assertIn(createdb('C:/0000/47python/zypyweb/db2207.db', 'test1', ['A', 'B', ]), [1, -1])
    #     self.assertIn(createdb('C:/0000/47python/zypyweb/db2207.db', 'test2', {'A': 'INTEGER', 'B': 'DATETIME', 'C': 'DATETIME1'}), [1, -1])

    # def test_insertdb1(self):
    #     self.assertEqual(insertdb1('C:/0000/47python/zypyweb/db2207.db', 'test1', ['A', 'B', ], [{'A': 1, 'B': 2}]), 1)
    #     self.assertEqual(insertdb1('C:/0000/47python/zypyweb/db2207.db', 'test1', ['A', 'B', ], [[3, 4]]), 1)
    #     self.assertEqual(insertdb1('C:/0000/47python/zypyweb/db2207.db', 'test1', ['A', 'B', ], [(5, 6)]), 1)

    # def test_createparams(self):
    #     result = createparams({'A': 'INTEGER', 'B': 'DATETIME', 'C': 'DATETIME1'}, ['B', 'A'])
    #     # print(result)
    #     self.assertEqual(result, ['DATETIME', 'INTEGER'])  # 可以
    #     result = createparams({'A': 'INTEGER', 'B': 'DATETIME', 'C': 'DATETIME1'}, ['B', 'A'], type=2)
    #     self.assertEqual(result, ('DATETIME', 'INTEGER'))  # 可以
    #     result = createparams(
    #         {'A': 'INTEGER', 'B': 'DATETIME', 'C': 'DATETIME1'},
    #         ['B', 'A', 'D'],
    #         type=3, defval='2222')
    #     self.assertEqual(result, {'B': 'DATETIME', 'A': 'INTEGER', 'D': '2222'})  # 可以

    def test_createsql(self):
        # 增
        self.assertEqual(createsql('tb0721', ['aid', 'gid'], type=1), 'insert into tb0721(aid,gid) values(?,?)')  # 可以
        # 导入
        self.assertEqual(createsql('tb0721', ['aid', 'gid'], type=11),
                         'insert into tb0721(aid,gid,importtime) values(?,?,\'' + time.strftime('%Y-%m-%d %H:%M:%S') + '\')')  # 可以
        # 删
        self.assertEqual(createsql('tb0721', ['aid', 'gid'], type=2), 'delete from tb0721 where id=?')  # 可以
        self.assertEqual(createsql('tb0721', ['aid', 'gid'], pk='aid', type=2), 'delete from tb0721 where aid=?')  # 可以
        # 改
        self.assertEqual(createsql('tb0721', ['aid', 'gid'], type=3), 'update tb0721 set aid=?,gid=? where id=?')  # 可以
        self.assertEqual(createsql('tb0721', ['aid', 'gid'], pk='aid', type=3), 'update tb0721 set aid=?,gid=? where aid=?')  # 可以
        self.assertEqual(createsql('tb0721', ['aid', 'gid'], pk='aid', type=33), 'update tb0721 set aid=:aid,gid=:gid where aid=:aid')  # 可以
        # 查
        self.assertEqual(createsql('tb0721', [], type=4), 'select * from tb0721')  # 可以
        self.assertEqual(createsql('tb0721', ['aid', 'gid'], type=4), 'select aid,gid from tb0721')  # 可以
        self.assertEqual(createsql('tb0721', ['aid', 'gid'], type=5), ' where aid=? and gid=?')  # 可以


if __name__ == '__main__':
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()
