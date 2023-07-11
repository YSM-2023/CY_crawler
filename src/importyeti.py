import requests
from bs4 import BeautifulSoup 
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from ast import literal_eval
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
import subprocess
import os
import pandas as pd
import csv


class ImportyetiCrawler:
    def __init__(self, file_name, save_dir) -> None:
        self.set_driver()
        self.save_dir = save_dir
        self.file_name = file_name
        self.set_csv()
    
    def set_driver(self):
        # subprocess.Popen(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument('--headless') #내부 창을 띄울 수 없으므로 설정
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
        self.driver.implicitly_wait(10)
        print("setted webdriver\n")

    def get_request(self, url, headers=""):
        self.driver.get(url)
        if headers=="":
            self.webpage = requests.get(url)
        else:
            self.webpage = requests.get(url, headers=literal_eval(headers))
        soup = BeautifulSoup(self.webpage.content, "html.parser")
        print("got request from website\n")
        return soup

    def __wait_until_find(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
            
    def __wait_and_click(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", button)

    def crawl(self, url, headers=""):
        soup = self.get_request(url, headers=headers)
        panel = self.__wait_until_find(self.driver, '//*[@id="headlessui-tabs-panel-30"]')

        page_li = panel.find_elements(By.XPATH, '*/li')
        page_max_num = int(page_li[-2].text)
        for i in range(page_max_num):
            panel = self.__wait_until_find(self.driver, '//*[@id="headlessui-tabs-panel-30"]')
            childElements = panel.find_elements(By.XPATH, '*')
            self.crawl_child_elements(childElements)
            if i == page_max_num-1:
                break
            self.driver.close()
            self.set_driver()
            url = url.replace(str(i), str(i+1))
            soup = self.get_request(url, headers)
            print(self.driver.current_url)
            time.sleep(15)
        self.driver.quit()

    def crawl_child_elements(self, childElements):
        name_li = []
        address_li = []
        info_li = []
        country_li = []
        source_li = []
        source = "importyeti"

        for i in range(0, len(childElements)):
            if i==len(childElements)-1:
                #다음 페이지 이동
                break
            if i>0:
                child = childElements[i].find_element(By.XPATH, '*/div[2]/div')
                childFlex = child.find_elements(By.XPATH, '*')
                #Buyer-name
                name_li.append(childFlex[0].text)
                #Buyer-address
                address_li.append(childFlex[1].text.replace('"', ''))
                #Buyer-info
                buyer_info = ""
                for i in range(5, len(childFlex)):
                    buyer_info += childFlex[i].text
                    if i<len(childFlex)-1: 
                        buyer_info += "|"
                info_li.append(buyer_info)
                #Buyer-country
                countryElement = child.find_element(By.XPATH, '*/strong/a/div')
                country_li.append(countryElement.get_attribute("class")[-2:])
                #Buyer-source
                source_li.append(source)
        self.save_csv(name_li, address_li, info_li, country_li, source_li)

    def save_csv(self, name_li, address_li, info_li, country_li, source_li):
        df = pd.DataFrame()
        df['name']= name_li
        df['address'] = address_li
        df['info'] = info_li
        df['country'] = country_li
        df['source'] = source_li
        print(df)
        df.to_csv(self.save_dir+self.file_name+".csv", index=False, header=False, mode='a')

    def set_csv(self):
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        columns=['name', 'address', 'info', 'country', 'source']
        f = open(self.save_dir+self.file_name+".csv", 'w', encoding='utf-8')
        write = csv.writer(f)
        write.writerow(columns)

if __name__ == '__main__':
    url = "https://www.importyeti.com/search?page=0&q=cosmetics"
    save_dir = 'importyetiData/'
    file_name = 'importyeti'

    crawler = ImportyetiCrawler(save_dir=save_dir, file_name=file_name)
    crawler.crawl(url=url)
