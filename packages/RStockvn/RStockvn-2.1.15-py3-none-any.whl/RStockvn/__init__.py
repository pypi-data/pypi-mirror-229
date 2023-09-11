# Copyright 2023 Nguyen Phuc Binh @ GitHub
# See LICENSE for details.
__version__ = "2.1.10.1"
__author__ ="Nguyen Phuc Binh"
__copyright__ = "Copyright 2023, Nguyen Phuc Binh"
__license__ = "MIT"
__email__ = "nguyenphucbinh67@gmail.com"
__website__ = "https://github.com/NPhucBinh"

from . import user_agent
from .chrome_driver.chromedriver_setup import check_var
from .stockvn import (report_finance_cf, get_price_history_cafef,get_insider_transaction_history_cafef,get_foreign_transaction_history_cafef,get_proprietary_history_cafef,
    lai_suat_cafef, getCPI_vietstock,solieu_GDP_vietstock, laisuat_vietstock, exchange_currency, tygia_vietstock, 
    solieu_XNK_vietstock, solieu_tindung_vietstock, solieu_sanxuat_congnghiep, solieu_banle_vietstock, solieu_danso_vietstock,solieu_FDI_vietstock,
    list_company,update_company,report_finance_vnd,key_id)

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

def setup_webdriver():
    try:
        driver = webdriver.Chrome()
    except Exception as e:
        print(f"Không tìm thấy ChromeDriver. Đang tự động tải và cài đặt...")
        ChromeDriverManager().install()
        driver = webdriver.Chrome()
    return driver
check_var()