##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：17
# 执行时间：2023-09-06 00:00:47
##################################################
from setuptools import setup, find_packages
from zypylibs.function.zycommon import updatedescribe

updatedescribe(__file__)


# with open("README.md", "r") as fh:
#     long_description = fh.read()

print(find_packages())

setup(
    name="ziyulibs",
    version="0.0.2",
    author="ziyu",
    author_email="89007524@qq.com",
    description="子煜python封装库",
    long_description="",
    long_description_content_type="text/markdown",
    packages=find_packages(),
)
