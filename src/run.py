from facebook import FacebookCrawler 
from googling import Googling 

import csv
from tqdm import tqdm
import json
import time
import ast
import pandas as pd
import os
from dotenv import load_dotenv
import warnings
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

warnings.filterwarnings('ignore')
options = Options()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
options.add_argument('user-agent=' + user_agent)
## for background
options.add_argument("--headless")
options.add_argument('--window-size=1920, 1080')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--start-maximized')
options.add_argument('--start-fullscreen')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('lang=en')
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

## For run the csv file and crawling the email
class Run:
    
    def __init__(self, save_path, driver):
        self.save_path = save_path
        self.driver = driver
        
        ## For facebook login
        load_dotenv()
        self.FACEBOOK_ID = os.environ.get('FACEBOOK_ID')
        self.FACEBOOK_PW = os.environ.get('FACEBOOK_PW')
        
    def __wait_until_find(self, driver, xpath):
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
    
    def __wait_until_find_classname(self, driver, classname):
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, classname)))
        element = driver.find_element(By.CLASS_NAME, classname)
        return element
    
    def __wait_and_click_classname(self, driver, classname):
        WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.CLASS_NAME, classname)))
        button = driver.find_element(By.CLASS_NAME, classname)
        driver.execute_script("arguments[0].click();", button)
        
    def click_escape_key(self, driver):
        ## When login popup shows
        try:
            action = ActionChains(driver)
            action.send_keys(Keys.ESCAPE).perform()
        except:
            print("Click Error")
    
    def run_facebook(self, facebook_page_url):
        ## For get facebook page email
        fc = FacebookCrawler('', self.driver)
        icon_list = fc.run_one(facebook_page_url)
        # print(facebook_page_url)
        
        ## Checking if email is in icon list
        if 'email' in icon_list.keys():
            return icon_list['email']
        else:
            return ''
        
    def run_one(self, website_url):
        googling = Googling(website_url)
        # print(website_url)
        
        ## Get facebook page url
        facebook_page_url = googling.run(self.driver)

        ## Get facebook email
        if facebook_page_url != '':
            return self.run_facebook(facebook_page_url)
        return ''
        
    def get_csv(self, file_path):
        ## Get CSV file
        csv_mapping_list = []
        with open(file_path, 'rt', encoding='UTF8') as my_data:
            csv_reader = csv.reader(my_data, delimiter=",")
            line_count = 0
            for line in csv_reader:
                if line_count == 0:
                    header = line
                else:
                    row_dict = {key: value for key, value in zip(header, line)}
                    csv_mapping_list.append(row_dict)
                line_count += 1
        # return csv_mapping_list[58:]
        return csv_mapping_list
    
    def save_data(self, csv_path, email_list):
        ## save all data
        exist_data = pd.read_csv(csv_path)
        exist_data.insert(1, 'email', email_list)
        
        self.save('new_cosmoprof_final.csv', exist_data)
    
    def save_temp(self, csv_path, email_list):
        ## save temp data
        exist_data = pd.read_csv(csv_path)
        exist_data = exist_data[:len(email_list)]
        # exist_data = exist_data[58:58+len(email_list)]
        exist_data.insert(1, 'email', email_list)
        
        self.save('new_cosmoprof2.csv', exist_data)  
        
    def save(self, file_name, dataframe):
        ## save to path
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)

        dataframe.to_csv(self.save_path+file_name, index = False)   
        
    def login(self):
        try:
            id_field = self.__wait_until_find(self.driver, '//*[@id="email"]')
            id_field.send_keys(self.FACEBOOK_ID)
            pw_field = self.__wait_until_find(driver, '//*[@id="pass"]')
            pw_field.send_keys(self.FACEBOOK_PW)
            self.__wait_and_click_classname(self.driver, '_42ft._4jy0._6lth._4jy6._4jy1.selected._51sy')
            self.click_escape_key(self.driver)
        except:
            print('Fail Login')
        
    def run(self, csv_path):
        
        #login facebook before start searching
        self.driver.get("https://facebook.com")
        self.login()
        
        ## Get csv list
        csv_mapping_list = self.get_csv(csv_path)

        email_list = []
        for row in tqdm(csv_mapping_list, desc='Get Email'):
            print(row['name'])
            sns_list = ast.literal_eval(row['sns'])
            
            ## When facebook url exist -> Directly get facebook email
            if sns_list[0] != '':
                email = self.run_facebook(sns_list[0])
                ## When facebook url is wrong -> find with website_url (googling)
                if email == '':
                    email = self.run_one(row['website'])
            ## When facebook url doesn't exist -> find with website_url (googling)
            else:
                email = self.run_one(row['website'])
            email_list.append(email)
            ## save one
            self.save_temp(csv_path, email_list)
        self.save_data(csv_path, email_list)
    
    
if __name__ == '__main__':
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
    website_url_list = ['http://azzurrabelli.it', 'http://www.thepuffcuff.com', 'http://zhenqingcosmetics.com/', 'https://purebrazilian.com/',\
        'http://www.pyramid-usa.com', 'https://pyurvana.com', 'http://www.hollyren.com', 'http://www.ibeautyac.com', \
        'http://www.isabella-lashes.com', 'http://www.lashnew.com', 'http://www.worldbeautyeyelashes.com ']
    
    run = Run('./', driver)
    run.run("cosmoprofData/cosmoprof.csv")
