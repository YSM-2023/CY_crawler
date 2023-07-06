import requests
from bs4 import BeautifulSoup
import time
import os
import warnings
from tqdm import tqdm
import logging
from dotenv import load_dotenv
# from lxml import etree
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

from facebook import FacebookCrawler 

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
# options.add_argument('--user-data-dir=./tmp_cache/bwj')

## For using PROXY (Not using now)
# webdriver.DesiredCapabilities.CHROME['proxy'] = {
#     "httpProxy": PROXY,
#     "ftpProxy": PROXY,
#     "sslProxy": PROXY,
#     "proxyType": "MANUAL"
# }
# webdriver.DesiredCapabilities.CHROME['acceptSslCerts']=True

## for Recaptcha-Solver
# options.add_extension('/Users/sunwookim/Library/Application Support/Google/Chrome/Default/Extensions/mpbjkejclgfgadiemmefgebjfooflfhl/2.0.1_0.crx')

## for english
options.add_argument('lang=en')
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

# Save log 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('googling.log')
logger.addHandler(file_handler)

## For Googling the facebook page
class Googling:
    
    def __init__(self, website_url):
        self.website_url = website_url
        
        load_dotenv()

        # ## For facebook login
        # self.FACEBOOK_ID = os.environ.get('FACEBOOK_ID')
        # self.FACEBOOK_PW = os.environ.get('FACEBOOK_PW')
        
    def __wait_until_find(self, driver, xpath):
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
    
    def __wait_until_find_classname(self, driver, classname):
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, classname)))
        element = driver.find_element(By.CLASS_NAME, classname)
        return element
            
    def __wait_and_click(self, driver, xpath):
        WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", button)
        
    def __wait_and_click_classname(self, driver, classname):
        WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.CLASS_NAME, classname)))
        button = driver.find_element(By.CLASS_NAME, classname)
        driver.execute_script("arguments[0].click();", button)
    
    def get_facebook_page(self, driver, website_url):
        facebook_page_url = ''
        
        ## For prevent wrong facebook page
        not_facebook_page_list = ['https://www.facebook.com/pages', 'https://www.facebook.com/business', 'https://www.facebook.com/help', \
            'https://www.facebook.com/public', 'https://www.facebook.com/facebook', '/posts/', '/photos/', '/shop/']
        
        html = driver.page_source
        soup = BeautifulSoup(html)
        cnt = 0
        result_list = soup.select_one('#rso')
        name_list = result_list.find_all('a')
        
        for name in name_list:
            check = True
            ## Get first facebook page
            if 'www.facebook.com' in name.get('href'):
                # print(name.get('href'))
                ##  Except error page
                for not_facebook_page in not_facebook_page_list:
                    if not_facebook_page in name.get('href'):
                        check = False
                        break
                    
                if check == True:
                    ## For prevent too many try.. (late time issue)
                    # if cnt >= 2:
                    #     break
                    # cnt += 1
                    
                    ## Checking the website url between DB and facebook -> prevent wrong info
                    if self.check_website_url(driver, name.get('href'), website_url)  == True:
                        facebook_page_url = name.get('href')
                        break
                
            # print(facebook_page_url)
        return facebook_page_url
    
    def check_website_url(self, driver, facebook_page_url, website_url):
        ## For checking the website url between DB and facebook
        
        ## Get facebook page's email
        fc = FacebookCrawler('', driver)
        icon_list = fc.run_one(facebook_page_url)
        # print(icon_list)
        
        ## Checking
        if facebook_page_url != '' and 'site_url' in icon_list.keys() and icon_list['site_url'] in website_url:
            return True
        return False
    
    def click_escape_key(self, driver):
        ## When login popup shows
        try:
            action = ActionChains(driver)
            action.send_keys(Keys.ESCAPE).perform()
        except:
            print("Click Error")
        
    # def login(self, driver):
        
    #     try:
    #         id_field = self.__wait_until_find(driver, '//*[@id="email"]')
    #         id_field.send_keys(self.FACEBOOK_ID)
    #         pw_field = self.__wait_until_find(driver, '//*[@id="pass"]')
    #         pw_field.send_keys(self.FACEBOOK_PW)
    #         self.__wait_and_click_classname(driver, '_42ft._4jy0._6lth._4jy6._4jy1.selected._51sy')
            
    #         self.click_escape_key(driver)
    #     except:
    #         print('Fail Login')
    
    def run(self, driver):
        # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        # #login facebook before start searching
        # driver.get("https://facebook.com")
        # self.login(driver)
        
        ## search keyword: facebook page {website url}
        ## add '&hl=en' to get result of english
        # facebook_page_urls=[]
        
        # for website_url in self.website_urls:
        search_url = 'https://www.google.com/search?q=facebook page '+ self.website_url + '&hl=en'
        
        driver.get(search_url)
        
        # time.sleep(3000)
        ## Get facebook page url
        facebook_page_url = self.get_facebook_page(driver, self.website_url)
        
        # facebook_page_urls.append(facebook_page_url)
            
        return facebook_page_url

if __name__ == '__main__':
    website_urls = ['http://www.ellamila.com','http://www.queenspack.com', 'http://www.innovatethelabel.com', 'http://www.celebluxury.com', 'http://www.raybae.com', 'https://purepapayacareusa.com', 'http://bebellacosmetics.com/', 'http://www.zoefountain.com', 'http://www.ameonskin.com', 'http://www.amazingshinenails.com']

    googling = Googling('http://www.ellamila.com')
    result = googling.run()
    print(result)