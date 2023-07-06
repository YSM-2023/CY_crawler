import requests
from bs4 import BeautifulSoup
import time
import os
import warnings
from tqdm import tqdm
import logging
from dotenv import load_dotenv
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert


warnings.filterwarnings('ignore')
options = Options()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
options.add_argument('user-agent=' + user_agent)
## for background
# options.add_argument("headless")
options.add_argument('--window-size=1920, 1080')
options.add_argument('--no-sandbox')
options.add_argument("--disable-dev-shm-usage")
# options.add_argument('--start-maximized')
# options.add_argument('--start-fullscreen')
options.add_argument('--disable-blink-features=AutomationControlled')

# Save log 
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# file_handler = logging.FileHandler('facebook.log')
# logger.addHandler(file_handler)

## For Crawling the Facebook page
class FacebookCrawler:
    
    def __init__(self, save_path):
        self.save_path = save_path
        
        load_dotenv()

        ## For facebook login
        self.FACEBOOK_ID = os.environ.get('FACEBOOK_ID')
        self.FACEBOOK_PW = os.environ.get('FACEBOOK_PW')
        
    def __wait_until_find(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
            
    def __wait_and_click(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", button)

    def get_icon(self, src):
        ## For make category using src of icon
        icon = ''
        if src in ['https://static.xx.fbcdn.net/rsrc.php/v3/yC/r/qF_eflLVarp.png', \
            'https://static.xx.fbcdn.net/rsrc.php/v3/ye/r/4PEEs7qlhJk.png']:
            icon = 'info'
        elif src in ['https://static.xx.fbcdn.net/rsrc.php/v3/y0/r/Oc_idC-xUXw.png', \
            'https://static.xx.fbcdn.net/rsrc.php/v3/yM/r/qUPkXkiEwfh.png']:
            icon = 'owner'
        elif src in ['https://static.xx.fbcdn.net/rsrc.php/v3/yr/r/bwmGKGh4YjO.png', \
            'https://static.xx.fbcdn.net/rsrc.php/v3/yW/r/8k_Y-oVxbuU.png']:
            icon = 'address'
        elif src in ['https://static.xx.fbcdn.net/rsrc.php/v3/yb/r/KVUi1wUrbfb.png', \
            'https://static.xx.fbcdn.net/rsrc.php/v3/yE/r/2PIcyqpptfD.png']:
            icon = 'email'
        elif src in ['https://static.xx.fbcdn.net/rsrc.php/v3/y4/r/UF-jk_lKW5x.png', \
            'https://static.xx.fbcdn.net/rsrc.php/v3/y3/r/BQdeC67wT9z.png']:
            icon = 'site_url'
        else:
            icon = 'etc'
        return icon
    
    def get_icon_desc(self, icon, text):
        ## For get icon description
        desc = ''
        if icon == 'info':
            desc = text.split('·')[1]
        elif icon == 'owner':
            desc = text.split('\n')[0]
        elif icon == 'address':
            desc = text
        elif icon == 'email':
            desc = text
        elif icon == 'site_url':
            desc = text
        return desc
    
    def get_icon_list(self, driver):
        ## Crawling the icons
        icon_list = {}
        icon_list_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/\
            div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/\
            div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul'
            
        try:
            icon_el_list = self.__wait_until_find(driver, icon_list_xpath)
        except:
            try:
                icon_list_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/\
                    div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/\
                    div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[1]/div/ul'
                icon_el_list = self.__wait_until_find(driver, icon_list_xpath)
            except:
                print("No List")
                return {}
        
        try:
            children = icon_el_list.find_elements(By.XPATH, './child::*')
            
            for elem in children:
                src = elem.find_element(By.XPATH, './div/img').get_attribute('src')
                # print(elem.text)
                icon = self.get_icon(src)
                if icon != 'etc':
                    desc = self.get_icon_desc(icon, elem.text)
                    icon_list[icon] = desc
        except:
            print("No List")
            return {}
            
        return icon_list
    
    def click_escape_key(self, driver):
        ## When login popup shows
        try:
            action = ActionChains(driver)
            action.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
        except:
            print("Click Error")
            
    def login(self, driver):
        ## When the page goes to login page
        try:
            id_field = self.__wait_until_find(driver, '//*[@id="email"]')
            id_field.send_keys(self.FACEBOOK_ID)
            pw_field = self.__wait_until_find(driver, '//*[@id="pass"]')
            pw_field.send_keys(self.FACEBOOK_PW)

            self.__wait_and_click(driver, '//*[@id="loginbutton"]')
            
        except:
            print('Fail Login')
            
    def get_driver(self, url):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        self.login(driver)
        
        return driver
    
    def run_one(self, url):
        
        ## Go to facebook page
        driver = self.get_driver(url)
        
        if 'https://www.facebook.com/login' in driver.current_url:
            return {}
        
        ## Close the login popup
        self.click_escape_key(driver)
        
        ## Get list of facebook page description
        icon_list = self.get_icon_list(driver)
        # print(icon_list)
        return icon_list
        
if __name__ == '__main__':
    save_path = 'FacebookData/'
    url_list = ['https://www.facebook.com/Solesence/', 'https://www.facebook.com/1821ManMade/', 'https://www.facebook.com/7emyolift/', 'https://www.facebook.com/love7thheaven']

    # Run FacebookCrawler with save_path
    fc = FacebookCrawler(save_path)
    
    icon_list = fc.run_one('https://www.facebook.com/Solesence/')
    print(icon_list)
    