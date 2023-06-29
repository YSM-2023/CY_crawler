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


class ImportyetiCrawler:
    def __init__(self) -> None:
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

    # def set_csv(self, id, table_name, cols):
    #     f_name = str(id)+".csv"
    #     f = open(f_name, 'w', encoding='utf-8')
    #     f.write(table_name+"\n")
    #     for col in cols:
    #         f.write(col)
    #         if not col is cols[-1]:
    #             f.write("|")
    #     f.write("\n")
    #     print("made csv file for saving crawled data\n")
    #     return f

    def __wait_until_find(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
            
    def __wait_and_click(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", button)

    def crawl_linkedin(self, url, headers=""):
        soup = self.get_request(url, headers=headers)
        print(self.driver.current_url)        

    def crawl(self, id, url, headers=""):
        soup = self.get_request(url, headers=headers)
        panel = self.__wait_until_find(self.driver, '//*[@id="headlessui-tabs-panel-30"]')

        # childElements = panel.find_elements(By.XPATH, '*')
        # print(len(childElements))

        page_li = panel.find_elements(By.XPATH, '*/li')
        page_max_num = int(page_li[-2].text)
        for i in range(page_max_num):
            panel = self.__wait_until_find(self.driver, '//*[@id="headlessui-tabs-panel-30"]')
            childElements = panel.find_elements(By.XPATH, '*')
            print(len(childElements))

            print("------------------------------------", i)
            print("\n")
            self.crawl_child_elements(childElements)
            if i == page_max_num-1:
                break
            # time.sleep(15)
            # print(page_li[-1].get_attribute("class"))
            # page_li[-1].click()
            # print("clicked!!!!")
            self.driver.close()
            self.__init__()
            url = url.replace(str(i), str(i+1))
            soup = self.get_request(url, headers)
            # self.driver.switch_to.window(self.driver.window_handles[-1])
            print(self.driver.current_url)
            # os.rmdir("C:\chrometemp")
            time.sleep(15)

    def crawl_child_elements(self, childElements):
        for i in range(0, len(childElements)):
            if i==len(childElements)-1:
                #다음 페이지 이동
                break
            if i>0:
                print("============", i)
                child = childElements[i].find_element(By.XPATH, '*/div[2]/div')
                childFlex = child.find_elements(By.XPATH, '*')
                print(len(childFlex))
                #Buyer-name
                print(childFlex[0].text)
                #Buyer-address
                print(childFlex[1].text)
                #Buyer-info
                print(childFlex[7].text+", "+childFlex[8].text+", "+childFlex[9].text)
                country = child.find_element(By.XPATH, '*/strong/a/div')
                print(country.get_attribute("class"))

                # 나중에 linkedin crawler 함수 호출
                linkedin_url = "https://www.linkedin.com/search/results/companies/?keywords=" + childElements[0].text.replace(' ', '%20')
                # self.crawl_linkedin(linkedin_url)
                



crawler = ImportyetiCrawler()
crawler.crawl(0, "https://www.importyeti.com/search?page=0&q=cosmetics")
# crawler.crawl(0, "https://www.importyeti.com/search?page=1&q=cosmetics", '{"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\AppleWebKit 537.36 (KHTML, like Gecko) Chrome",	"Accept":"text/html,application/xhtml+xml,application/xml;\q=0.9,imgwebp,*/*;q=0.8"}')
