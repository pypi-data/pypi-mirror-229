##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：205
# 执行时间：2023-09-08 11:59:39
##################################################
import xml.dom.minidom
from xml.dom.minidom import parse
import xml.sax
from ziyulibs.function.zycommon import updatedescribe
updatedescribe(__file__)


# path = r'C:\Users\86186\Desktop\20221010宠物资料 - 副本\批量导出_20221014130036\自动追踪_20221007091152872\自动追踪_20221007091152872.kml'

# DOMTree = xml.dom.minidom.parse(path)
# collection = DOMTree.documentElement
# if collection.hasAttribute('name'):
#     print('Root element : %s' % collection.getAttribute('name'))


# elements = collection.getElementsByTagName("Data")

# Data
# print(elements,name='name',value='lineType')


def findelements(elements, attrname='name', attrvalue='lineType'):
    """_summary_

    Args:
        elements (_type_): _description_
        attrname (str, optional): _description_. Defaults to 'name'.
        attrvalue (str, optional): _description_. Defaults to 'lineType'.

    Returns:
        _type_: _description_
    """
    ls = []
    elements = collection.getElementsByTagName("Data")
    for element in elements:
        if (element.hasAttribute(attrname)):
            if (element.getAttribute(attrname) == attrvalue and attrvalue != None):
                ls.append(element)
            else:
                ls.append(element)

    return ls
