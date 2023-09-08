##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：0
# 执行时间：2023-01-07 22:09:12
##################################################
from numpy import array
import unittest

# from zypylibs.function.zycommon import updatecomment, updatedescribe  #


def filterarray(paramsfields, configfields):
    """过滤数据中的数据,返回新的数组

    Args:
        paramsfields (_type_): _description_
        configfields (_type_): _description_

    Returns:
        _type_: _description_
    """
    return [val for val in paramsfields if val in configfields]


def mergearray(data):
    """合并数组集合,返回一个新的数组

    Args:
        data (_type_): 数组集合

    Returns:
        _type_: _description_
    """
    return [y for x in data for y in x]


def mergearray1(data):
    """合并数组集合,返回一个新的数组

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    return list(array(data).flatten())


def pluckarray(ls, key):
    """提取字典集合中指定的key,生成新的集合

    Args:
        ls (_type_): _description_
        key (_type_): _description_
    """
    # print(type(key).__name__)
    return list(map(lambda m: m[key], ls))
    # if (type(key).__name__ == ''):
    #     return list(map(lambda m: m[key], ls))
    # else:
    #     return list(map(lambda m: m[key], ls))


def removearray(ls, ls2):
    return list(filter(lambda m: m not in ls2, ls))


def _lambdaindex(data):
    """测试lambda表达式的index

    解决办法:要使用enumerate
    """
    # 这个方式不行,只能接收一个参数,那就只能通过m的索引来取,或者在后方传入两个数组,那就有了两种解决方案
    # return list(map(lambda m, i: (m, i), enumerate(['A', 'B', 'C'])))

    # 方案1
    # return list(map(lambda m, i: (m, i), data, range(len(data))))
    # 方案2
    # return list(map(lambda m: (list(m)[1], list(m)[0]), enumerate(data)))
    return list(map(lambda m: (m[1], m[0]), enumerate(data)))  # 不用转数组也行
    # 结论 显然方案1好一些


class zyarr(unittest.TestCase):

    def test_filterarray(self):
        self.assertEqual(filterarray([1, 2, 3, 4, 5], [1, 2, 3, 9]), [1, 2, 3])

    def test_mergearray(self):
        result = mergearray([[1, 2, 3], [11, 22, 33]])
        self.assertEqual(result, [1, 2, 3, 11, 22, 33])

    def test_mergearray1(self):
        result = mergearray1([[1, 2, 3], [11, 22, 33]])
        self.assertEqual(result, [1, 2, 3, 11, 22, 33])

    def test_pluckarray(self):
        result = pluckarray([{"A": "10"}, {"A": "11"}], "A")
        self.assertEqual(result, ["10", "11"])

    def test__lambdaindex(self):
        result = _lambdaindex(["A", "B", "C"])
        self.assertEqual(result, [("A", 0), ("B", 1), ("C", 2)])


if __name__ == "__main__":
    # updatecomment(__file__)
    # updatedescribe(__file__)
    unittest.main()
