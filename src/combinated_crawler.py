import requests
from bs4 import BeautifulSoup 
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from ast import literal_eval


class Crawler:
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

    def set_txt(self, id, table_name, cols):
        f_name = str(id)+".txt"
        f = open(f_name, 'w', encoding='utf-8')
        f.write(table_name+"\n")
        for col in cols:
            f.write(col)
            if not col is cols[-1]:
                f.write("|")
        f.write("\n")
        print("made csv file for saving crawled data\n")
        return f

    def crawl_1(self, id, url, headers=""):
        soup = self.get_request(url, headers=headers)

        table = soup.find("table", attrs={"class":"table table-striped table-hover table-bordered"})
        tbody = table.select_one('tbody')
        trs = tbody.select('tr')

        table_name = "company"
        cols = ["name", "address", "type", "owner"]
        f = self.set_txt(id, table_name, cols)
        for tr in trs:
            name = tr.select('td')[0].text.strip()
            address = tr.select('td')[1].text.strip()
            type = tr.select('td')[2].text.strip()
            owner = tr.select('td')[3].text.strip()
            f.write(name+"|"+address+"|"+type+"|"+owner+"\n")            
        f.close()

    def crawl_2(self, id, url, headers=""):
        soup = self.get_request(url, headers=headers)
        frame = soup.find('iframe', attrs={"class":"iframe-class"})

        frame_soup = self.get_request(frame['src'])
        frame2 = frame_soup.find('frame')

        table_name = "company"
        cols = ["name", "description"]
        f = self.set_txt(id, table_name, cols)

        # selenuim으로 기업명 저장 및 기업명 클릭 후 상세 설명 저장
        self.driver.get(frame2['src'])
        sample = self.driver.find_elements(By.CLASS_NAME, "ex")
        for item in sample:
            f.write(item.text.strip()+"|") # 기업명 저장
            item.send_keys('\n') # 클릭
            time.sleep(2)
            desc = self.driver.find_element(By.XPATH, '//*[@id="profileTab"]/div')
            f.write(desc.text.replace("\n"," ")+"\n") # 기업 상세 설명 저장
        f.close()        

    def crawl_3(self, id, url, headers=""):
        self.get_request(url, headers)
        cookieBtn = self.driver.find_element(By .XPATH, '//*[@id="didomi-notice-agree-button"]').click()

        gridBox = self.driver.find_element(By .XPATH, '//*[@id="content"]/div/div[1]/section[6]/div/div/div/div[3]/div/div/div')
        gridElements = gridBox.find_elements(By .CLASS_NAME, 'ex_name')
        
        table_name = "company"
        cols = ["name"]
        f = self.set_txt(id, table_name, cols)
        for gridElement in gridElements:
            f.write(gridElement.text+"\n")
        f.close()

