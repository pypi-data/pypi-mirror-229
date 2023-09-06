##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：0
# 执行时间：2023-01-07 22:09:12
##################################################
import unittest
# from zypylibs.function.zycommon import updatecomment, updatedescribe  #


def datatype(data, type=False):

    if (isinstance(data, int)):
        if (type):
            return 'base'
        return 'int'
    if (isinstance(data, str)):
        if (type):
            return 'base'
        return 'str'
    if (isinstance(data, float)):
        if (type):
            return 'base'
        return 'float'
    # if (isinstance(data,long)): #python3 中没有Long类型
    #     if (type):
    #         return 'base'
    #     return 'str'
    if (isinstance(data, dict)):
        return 'dict'
    if (isinstance(data, list)):
        s = set({})
        if(type):
            s.update(list(map(lambda x: datatype(x, True), data)))
            s = list(s)
            if(len(s) == 1):
                return 'list'+s[0]
            else:
                return 'list'
            #  return s
        return 'list'
    if (isinstance(data, tuple)):
        return 'tuple'


class zytype(unittest.TestCase):
    def test_datatype(self):

        # print(str(type('1')))
        # print(str(type(True)))
        # print(str(type(None)))
        # print(str(type([])))
        # print(str(type({})))

        # print(isinstance('', str))
        # print(isinstance(1, int))
        # print(isinstance(True, int))
        # # print(isinstance(None,NoneType))
        # print(isinstance([], list))
        # print(isinstance({}, dict))

        self.assertEqual(datatype(1), 'int')
        self.assertEqual(datatype('123'), 'str')
        self.assertEqual(datatype(1.0), 'float')
        self.assertEqual(datatype({}), 'dict')
        self.assertEqual(datatype([1, '2', 3.0]), 'list')
        self.assertEqual(datatype((1, 2, 3)), 'tuple')
        self.assertEqual(datatype([1, '2', 3.0], True), 'listbase')
        self.assertEqual(datatype([{}, {}, {}], True), 'listdict')
        self.assertEqual(datatype([(1, 2, 3), (1, 2, 3)], True), 'listtuple')
        self.assertEqual(datatype([[1, 2, 3], [1, 2, 3]], True), 'listlistbase')


if __name__ == '__main__':
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()
