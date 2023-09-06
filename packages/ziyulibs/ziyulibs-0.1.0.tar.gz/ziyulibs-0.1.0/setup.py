from setuptools import setup, find_packages

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

print(find_packages())

setup(
    name="ziyulibs",
    version="0.1.0",
    author="june",
    packages=find_packages(),
    # py_modules=["mypackage"],
    description="子煜的封装库",
    #     install_requires=[
    #         # 在这里列出你的库所需的其他Python包
    #     ],
    #     author_email="your.email@example.com",
    #     description="A short description of your awesome package",
    #     long_description=open("README.md").read(),
    #     long_description_content_type="text/markdown",
    #     license="MIT",
    #     url="https://github.com/yourusername/my-awesome-package",
    #     classifiers=[
    #         "Development Status :: 3 - Alpha",
    #         "Intended Audience :: Developers",
    #         "License :: OSI Approved :: MIT License",
    #         "Programming Language :: Python",
    #         "Programming Language :: Python :: 3",
    #         "Programming Language :: Python :: 3.6",
    #         "Programming Language :: Python :: 3.7",
    #         "Programming Language :: Python :: 3.8",
    #         "Programming Language :: Python :: 3.9",
    # ]
)


# setuptools.setup(
#     name="mwj-apitest",  # 用自己的名替换其中的YOUR_USERNAME_
#     version="1.0.0",  # 包版本号，便于维护版本,保证每次发布都是版本都是唯一的
#     author="梦无矶小仔",  # 作者，可以写自己的姓名
#     author_email="Lvan826199@163.com",  # 作者联系方式，可写自己的邮箱地址
#     description="A small example package",  # 包的简述
#     long_description=long_description,  # 包的详细介绍，一般在README.md文件内
#     long_description_content_type="text/markdown",
#     url="https://github.com/Lvan826199/mwjApiTest",  # 自己项目地址，比如github的项目地址
#     packages=setuptools.find_packages(),
#     entry_points={
#         "console_scripts": ["mwjApiTest = mwjApiTest.manage:run"]
#     },  # 安装成功后，在命令行输入mwjApiTest 就相当于执行了mwjApiTest.manage.py中的run了
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
#         "Operating System :: OS Independent",
#     ],
#     python_requires=">=3.6",  # 对python的最低版本要求
# )
