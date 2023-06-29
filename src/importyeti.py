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


class ImportyetiCrawler:
    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument('--headless') #내부 창을 띄울 수 없으므로 설정
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
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
        childElements = panel.find_elements(By.XPATH, '*')
        print(len(childElements))
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

                # detailClick = child.find_element(By.CSS_SELECTOR, 'a')
                # print(detailClick.text)
                # print(detailClick.get_attribute("href"))
                # detailClick.click()
                # print(self.driver.current_url)
                # time.sleep(30)
                linkedin_url = "https://www.linkedin.com/search/results/companies/?keywords=" + childElements[0].text.replace(' ', '%20')
                self.crawl_linkedin(linkedin_url)
                break
                



crawler = ImportyetiCrawler()
crawler.crawl(0, "https://www.importyeti.com/search?page=1&q=cosmetics")
