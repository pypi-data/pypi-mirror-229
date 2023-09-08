# Copyright 2023 Nguyen Phuc Binh @ GitHub
# See LICENSE for details.
from setuptools import setup, find_packages
from Cython.Build import cythonize
import os
import codecs

hs = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(hs, 'README.md'), encoding='utf-8') as fh:
    long_description = fh.read()

DS = 'Report Finance of Companies in Vietnamese and macro data - Lấy báo cáo tài chính của các công ty ở Việt Nam và số liệu vĩ mô'

# Thêm tất cả các tệp .pyx vào danh sách
cython_modules = [
    'RStockvn/__init__.pyx',
    'RStockvn/cafef_test.pyx',
    'RStockvn/chromedriver_setup.pyx',
    'RStockvn/ds_company.pyx',
    'RStockvn/ls_cafef.pyx',
    'RStockvn/report_vnd.pyx',
    'RStockvn/stockvn.pyx',
    'RStockvn/user_agent.pyx',
]

# Biên dịch các tệp .pyx thành tệp .pyd
ext_modules = cythonize(cython_modules)

# Setting
setup(
    name='RStockvn',
    version='2.1.10.36',
    author='NGUYEN PHUC BINH',
    author_email='nguyenphucbinh67@gmail.com',
    description=DS,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    package_data={'RStockvn': ['data/*.xlsx', 'chrome_driver/*/*']},
    ext_modules=ext_modules,  # Thêm các mô-đun Cython đã biên dịch
    url="https://github.com/NPhucBinh/RStockvn",
    install_requires=[
        'pandas', 'requests', 'jsonschema', 'bs4', 'selenium', 'undetected_chromedriver',
        'webdriver_manager', 'html5lib', 'lxml', 'jsons', 'unidecode', 'urllib3', 'gdown',
        'cryptography', 'chromedriver_autoinstaller', 'cython'
    ],
    keywords=[
        'stockvn', 'rpv', 'rstockvn', 'report stock vn', 'báo cáo tài chính việt nam',
        'lấy báo cáo tài chính việt nam bằng python', 'lấy báo cáo tài chính về excel',
        'lấy báo cáo tài chính về excel bằng python'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
