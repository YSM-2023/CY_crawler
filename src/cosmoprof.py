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


class CosmoprofCrawler:

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
            
    def get_data(self, driver):
        driver.switch_to.window(driver.window_handles[-1])
        self.__wait_until_find_classname(driver,"BoothContactCountry")
        
        country = driver.find_element(By.CLASS_NAME, 'BoothContactCountry').text
        website = driver.find_element(By.CLASS_NAME, "BoothContactUrl").text
        
        # sns=[]
        # sns=[facebook,twitter,linkedin,instagram]
        sns=['','','','']
        try:
            sns_list = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ctrlCustomField_Logos_dlCustomFieldList").find_elements(By.TAG_NAME,"a")
            for item in sns_list: 
                icon_id=item.get_attribute("id")
                if icon_id=="ctl00_ContentPlaceHolder1_ctrlCustomField_Logos_dlCustomFieldList_ctl00_lnkCustomField":
                    sns[0]=item.get_attribute("href")
                elif icon_id=="ctl00_ContentPlaceHolder1_ctrlCustomField_Logos_dlCustomFieldList_ctl01_lnkCustomField":
                    sns[1]=item.get_attribute("href")
                elif icon_id=="ctl00_ContentPlaceHolder1_ctrlCustomField_Logos_dlCustomFieldList_ctl02_lnkCustomField":
                    sns[2]=item.get_attribute("href")
                elif icon_id=="ctl00_ContentPlaceHolder1_ctrlCustomField_Logos_dlCustomFieldList_ctl03_lnkCustomField":
                    sns[3]=item.get_attribute("href")
        except:
            pass
        
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        
        return country, website, sns
        
        
    def run(self):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        driver.get(self.url)
        
        # 쿠키 허용
        driver.find_element(By.CLASS_NAME, "cc-compliance").click()
        
        companies=driver.find_elements(By.CLASS_NAME, "exhibitorName")
        # ActionChains(driver).move_to_element(names[0]).perform()
        
        ## beautifulSoup
        # webpage=requests.get(self.url)
        # soup=BeautifulSoup(webpage.content, "html.parser")
        # names = soup.find_all("a", {"class":"exhibitorName"})
                

        # f = open("cosmoprof.txt", 'w', encoding='utf-8')
        # print(companies[0].text)
        for company in companies:   
            # webpage=requests.get(name["href"])
            # soup=BeautifulSoup(webpage.content, "html.parser")
            # country = soup.find("span", {"class":"BoothContactCountry"}).text
            # website = soup.find("a", {"class":"BoothContactUrl"}).text
            # sns = soup.find_all("span", {"class":"spCustomFieldIcon"})
            # print(country,website, sns)
            
            name=company.text.strip()
            
            # 기업명 클릭
            company.click()
            
            country, website, sns = self.get_data(driver)
            
            print('|', name,'|', country,'|', website,'|', sns)
            
    

        driver.quit()

        return name, country, website, sns
    
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
    url="https://s23.a2zinc.net/clients/pba/cosmoprof2022/Public/Exhibitors.aspx?Index=All"
    save_path = 'cosmoprofData/'
    
    # Run Crawler with save_path
    cc = CosmoprofCrawler(url, save_path)
    
    # Run Only One Project  
    name, country, website, sns = cc.run()
    # ccc.save_data(name, sns)
            