##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：217
# 执行时间：2023-09-08 11:59:37
##################################################
import unittest
import csv
from zypylibs.function.zycommon import updatedescribe
updatedescribe(__file__)

# csv文件转成数组,实际上就是使用固定字符拆分,然后以表头为key,记录为value返回字典集合


def readcsv(filename):
    # open的第一个参数为文件名，第二个参数为打开的类型"r"为读,'w'为写，'a'为追加等等
    csvFile = open(filename, "r")
    reader = csv.reader(csvFile)
    # 将reader转化为list,方便进行遍历
    listReader = list(reader)
    # 对reader进行按行遍历
    for row in listReader:
        print(row)


def csv2list(content, rowsplit='\n', colsplit='\t'):
    """csv 转 数组

    Args:
        content (_type_): _description_

    Returns:
        _type_: _description_
    """
    records = content.split(rowsplit)
    headers = records[0].split(colsplit)

    datalist = []
    for idx1, record in enumerate(records[1:]):
        dataitem = {}
        dataline = record.split(colsplit)
        for idx2, title in enumerate(headers):
            if (title == ''):
                continue
            dataitem[title] = dataline[idx2]
        datalist.append(dataitem)
    return datalist


def list2csv(datalist):
    """_summary_

    Args:
        datalist (_type_): _description_

    Returns:
        _type_: _description_
    """
    headers = []
    for dateitem in datalist:
        for key in dateitem.keys():
            if key not in headers:
                headers.append(key)
    datalst = []
    for idx1, dateitem in enumerate(datalist):
        if (idx1 == 0):
            datarow = []
            for title in (headers):
                datarow.append(title)
            datalst.append('\t'.join(datarow))
        datarow = []
        for title in (headers):
            datarow.append(str(dateitem[title]) if title in dateitem else '---')
        datalst.append('\t'.join(datarow))
    return '\n'.join(datalst)


class zycsv(unittest.TestCase):

    def test_csv2list(self):
        result = csv2list(
            '''证券代码\t证券名称\t股票余额\t可用余额\t冻结数量\t成本价\t市价\t盈亏\t盈亏比例(%)\t 当日盈亏\t当日盈亏比(%)\t市值\t仓位占比(%)\t当日买入\t当日卖出\t交易市场\t持股天数
601117\t中国化学\t100\t100\t0\t8.340\t7.950\t-45.020\t-4.680\t-2.00\t-0.25\t795.000\t0.38\t0\t0\t上海Ａ股\t4
603918\t金桥信息\t500\t500\t0\t6.670\t6.540\t-73.540\t-1.931\t-5.00\t-0.15\t3270.000\t1.56\t0\t0\t上海Ａ股\t5''')
        # print(result)
        self.assertEqual(len(result), 2)

    def test_list2csv(self):
        result = list2csv(
            [{'证券代码': '601117', '证券名称': '中国化学', '股票余额': '100', '可用余额': '100', '冻结数量': '0',
              '成本价': '8.340', '市价': '7.950', '盈亏': '-45.020', '盈亏比例(%)': '-4.680', ' 当日盈亏': '-2.00',
              '当日盈亏比(%)': '-0.25', '市值': '795.000', '仓位占比(%)': '0.38', '当日买入': '0', '当日卖出': '0',
              '交易市场': '上海Ａ股', '持股天数': '4'},
             {'证券代码': '603918', '证券名称': '金桥信息', '股票余 额': '500', '可用余额': '500', '冻结数量': '0',
              '成本价': '6.670', '市价': '6.540', '盈亏': '-73.540', '盈亏比例(%)': '-1.931', ' 当日盈亏': '-5.00',
              '当日盈亏比(%)': '-0.15', '市值': '3270.000', '仓位 占比(%)': '1.56', '当日买入': '0', '当日卖出': '0',
              '交易市场': '上海Ａ股', '持股天数': '5'}])
        # print(result)
        # print(len(result))
        self.assertEqual(len(result), 290)


if __name__ == '__main__':
    unittest.main()
