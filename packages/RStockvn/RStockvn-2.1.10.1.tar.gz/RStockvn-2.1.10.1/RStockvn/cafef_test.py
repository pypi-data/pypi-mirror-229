# Copyright 2023 Nguyen Phuc Binh @ GitHub
# See LICENSE for details.
__version__ = "2.1.8"
__author__ ="Nguyen Phuc Binh"
__copyright__ = "Copyright 2023, Nguyen Phuc Binh"
__license__ = "MIT"
__email__ = "nguyenphucbinh67@gmail.com"
__website__ = "https://github.com/NPhucBinh"
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import sys
import time
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())

class browser_get_data():
    
    def __init__(self,mck,fromdate,todate):
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from .user_agent import random_user
        self.useragent=random_user()
        self.url='https://s.cafef.vn/Lich-su-giao-dich-VNINDEX-1.chn#data'
        self.opt=Options()
        self.opt.add_argument('--headless')
        self.opt.add_argument('--dark-mode-settings')
        self.opt.add_argument("--incognito")
        self.opt.add_argument('--disable-gpu')
        self.opt.add_argument('--no-default-browser-check')
        self.opt.add_argument("user-agent=Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; ko; rv:1.9.1b2) Gecko/20081201")
        self.br=webdriver.Chrome(options=self.opt)
        self.br.maximize_window()
        self.br.get(self.url)
        self.mcp=self.br.find_element(By.ID,'ContentPlaceHolder1_ctl00_acp_inp_disclosure')
        self.mcp.clear()
        self.mcp.send_keys(mck)
        self.br.find_element(By.ID,'date-inp-disclosure').send_keys(f'{fromdate} - {todate}')
        ### javscipt
        apply_button = self.br.find_element(By.CLASS_NAME, 'applyBtn')
        self.br.execute_script("arguments[0].click();", apply_button)
        self.br.find_element(By.ID, 'owner-find').click()
        
    def number_of_pages(self):
        try:
            # Wait for the pagination elements to be present
            WebDriverWait(self.br, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'pagination-item')))
            
            pagination_items = self.br.find_elements(By.CLASS_NAME, 'pagination-item')
            
            # Extract page numbers as integers
            page_numbers = [int(item.text.strip()) for item in pagination_items if item.text.strip().isdigit()]
        except:
            WebDriverWait(self.br, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'pagination-item')))
            
            pagination_items = self.br.find_elements(By.CLASS_NAME, 'pagination-item')
            
            # Extract page numbers as integers
            page_numbers = [int(item.text.strip()) for item in pagination_items if item.text.strip().isdigit()]
        return max(page_numbers)


    def getdata(self):
        self.lis=[]
        self.end_page=self.number_of_pages()
        self.count=0
        while self.count!=self.end_page:
            time.sleep(0.6)
            self.br.find_element(By.ID,'paging-right').click()
            df=self.dataframe()
            self.lis.append(df)
            self.count+=1
        data=pd.concat(self.lis)
        data.rename(columns={'Giá (nghìn VNĐ)':'Giá Đóng cửa','Giá (nghìn VNĐ).1':'Giá Điều chỉnh',
                             'GD khớp lệnh':'KLGD khớp lệnh','GD khớp lệnh.1':'GTGD khớp lệnh',
                             'GD thỏa thuận':'KLGD thỏa thuận','GD thỏa thuận.1':'GTGD thỏa thuận',
                             'Giá (nghìn VNĐ).2':'Giá Mở cửa','Giá (nghìn VNĐ).3':'Giá Cao nhất',
                             'Giá (nghìn VNĐ).4':'Giá thấp nhất'}, inplace=True)
        #self.close()
        return data.reset_index(drop=True)
    
    def dataframe(self):
        import pandas as pd
        df=pd.read_html(self.br.page_source,encoding='utf-8',header=0)
        data=pd.DataFrame(df[1])
        data=data.drop(index=0)
        return data

    
    def close(self):
        self.br.quit()