from setuptools import setup, find_packages

with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # pip install nn
    name="WeReadScan-HTML",
    version="0.1.1",
    keywords=("weread", "scan", "pdf", "convert", "selenium"),
    description="WeRead HTML Scanner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # 协议
    license="GPL Licence",

    url="https://github.com/Algebra-FUN/WeReadScan/tree/html-variant",
    author="Algebra-FUN",
    author_email="algebra-fun@outlook.com",

    # 自动查询所有"__init__.py"
    packages=find_packages(),
    include_package_data=True,
    platforms=["windows","macos","linux"],
    # 提示前置包
    install_requires=['selenium', 'numpy', 'matplotlib'],
    python_requires='>=3.6'
)