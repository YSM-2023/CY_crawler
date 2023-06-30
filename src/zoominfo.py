import requests
from bs4 import BeautifulSoup
import time
import os
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from tqdm import tqdm
import time
import logging
import subprocess


warnings.filterwarnings('ignore')
options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
options.add_argument('user-agent=' + user_agent)
# ## for background
# options.add_argument("headless")
# options.add_argument('--window-size=1920, 1080')
# options.add_argument('--no-sandbox')
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument('--start-maximized')
# options.add_argument('--start-fullscreen')
# options.add_argument('--disable-blink-features=AutomationControlled')

# # Save log
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# file_handler = logging.FileHandler('codechef.log')
# logger.addHandler(file_handler)

# 쿠키 저장
subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\user\Desktop\CY\chromeCookie"')


class ZoominfoCrawler:

    def __init__(self, url, save_path):
        self.url = url        
        self.save_path = save_path
        
    def __wait_until_find_xpath(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
    
    def __wait_until_find_classname(self, driver, classname):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, classname)))
        element = driver.find_element(By.CLASS_NAME, classname)
        return element
    
    def __wait_until_find_tagname(self, driver, tagname):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, tagname)))
        element = driver.find_element(By.TAG_NAME, tagname)
        return element
    
    def __wait_until_find_id(self, driver, id):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, id)))
        element = driver.find_element(By.ID, id)
        return element
            
    def __wait_and_click(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", button)
        
    # def save_data(self, id, status, username, code, extension):
    #     # Save Code
    #     status = "".join([word.upper() for word in status if word.strip()])
    #     if status in ["AC"]:
    #         result = "correct"
    #     elif status in ["WA", "PAC"]:
    #         result = "wrong"
    #     else:
    #         result = "error"
    #     dir_path = os.path.join(self.save_path)
    #     file_path = dir_path+'/'+str(id)+'&'+status+'&'+str(username)+extension
    #     self.save(dir_path, file_path, code)    
    
    # def save(self, dir_path, file_path, data):
    #     if not os.path.isdir(dir_path):
    #         os.makedirs(dir_path)
    #     with open(file_path, 'w') as w:
    #         w.write(data.strip())
    
    def verify_human(self, driver):
        iframe_src=self.__wait_until_find_tagname(driver,"iframe").get_attribute("src")
        driver.get(iframe_src)
        challenge_stage=self.__wait_until_find_id(driver,"challenge-stage") 
        # //*[@id="challenge-stage"]/div/label/input
        # "ctp-checkbox-container"
        challenge_stage.find_element(By.TAG_NAME,"div").click()
        time.sleep(3)
            
    def get_data(self, driver):
        driver.switch_to.window(driver.window_handles[-1])
        self.__wait_until_find_classname(driver,"BoothContactCountry")
        
        country = driver.find_element(By.XPATH, '//*[@id="eboothContainer"]/div[2]/div/div[1]/span[1]').text
        website = driver.find_element(By.CLASS_NAME, "BoothContactUrl").text
        
        sns=[]
        try:
            sns_list = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ctrlCustomField_Logos_dlCustomFieldList").find_elements(By.TAG_NAME,"a")
            for item in sns_list: 
                sns.append(item.get_attribute("href"))
        except:
            pass
        
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        
        return country, website, sns
        
        
    def run(self):
        # debugger모드로 크롬 열기
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        driver.get(self.url)
        print("GET")
        
        companies=driver.find_elements(By.CLASS_NAME, "tableRow_companyName_nameAndLink")
        # ActionChains(driver).move_to_element(companies[0]).perform()

        # f = open("cosmoprof.txt", 'w', encoding='utf-8')
        for company in companies:   
            name=company.find_element(By.TAG_NAME, "a")
            
            # 기업명 클릭
            name.click()
            self.verify_human(driver)
            country, website, sns = self.get_data(driver)
            
            name=name.text.strip()
            print(name)
            # print('|', name,'|', country,'|', website,'|', sns)
            
    

        driver.quit()

        return name
    
    # def set_txt(self, id, table_name, cols):
    #     f_name = str(id)+".txt"
    #     f = open(f_name, 'w', encoding='utf-8')
    #     f.write(table_name+"\n")
    #     for col in cols:
    #         f.write(col)
    #         if not col is cols[-1]:
    #             f.write("|")
    #     f.write("\n")
    #     return f
            
        
        
if __name__ == '__main__':
    url="https://www.zoominfo.com/people-search/--Beauty+Buyer"
    save_path = 'zoominfoData/'
    
    # Run Crawler with save_path
    zc = ZoominfoCrawler(url, save_path)
    
    # Run Only One Project  
    name, sns = zc.run()
    # ccc.save_data(name, sns)