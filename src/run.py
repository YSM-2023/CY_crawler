from facebook import FacebookCrawler 
from googling import Googling 

import csv
from tqdm import tqdm
import json
import ast
import pandas as pd
import os

class Run:
    
    def __init__(self, save_path):
        self.save_path = save_path
        
    def run_one(self, website_url):
        googling = Googling(website_url)
        # print(website_url)
        
        facebook_page_url = googling.run_one()

        if facebook_page_url != '':
            return self.run_facebook(facebook_page_url)
        return ''
    
    def run_facebook(self, facebook_page_url):
        fc = FacebookCrawler('')
        icon_list = fc.run_one(facebook_page_url)
        # print(facebook_page_url)
        
        if 'email' in icon_list.keys():
            return icon_list['email']
        else:
            return ''
        
    def get_csv(self, file_path):
        csv_mapping_list = []
        with open(file_path) as my_data:
            csv_reader = csv.reader(my_data, delimiter=",")
            line_count = 0
            for line in csv_reader:
                if line_count == 0:
                    header = line
                else:
                    row_dict = {key: value for key, value in zip(header, line)}
                    csv_mapping_list.append(row_dict)
                line_count += 1
        return csv_mapping_list
        # return csv_mapping_list[17:] ## reset
    
    def save_data(self, csv_path, email_list):
        exist_data = pd.read_csv(csv_path)
        exist_data.insert(1, 'email', email_list)
        
        self.save('new_cosmoprof_final.csv', exist_data)
    
    def save_temp(self, csv_path, email_list):
        exist_data = pd.read_csv(csv_path)
        exist_data = exist_data[:len(email_list)]
        exist_data.insert(1, 'email', email_list)
        
        self.save('new_cosmoprof2.csv', exist_data)  
        
    def save(self, file_name, dataframe):
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)

        dataframe.to_csv(self.save_path+file_name, index = False)   
        
    def run(self, csv_path):
        csv_mapping_list = self.get_csv(csv_path)
    
        email_list = []
        for row in tqdm(csv_mapping_list, desc='Get Email'):
            print(row['name'])
            sns_list = ast.literal_eval(row['sns'])
            if sns_list[0] != '':
                email = self.run_facebook(sns_list[0])
                if email == '':
                    email = self.run_one(row['website'])
            else:
                email = self.run_one(row['website'])
            email_list.append(email)
            self.save_temp(csv_path, email_list)
        self.save_data(csv_path, email_list)
    
    
if __name__ == '__main__':
    
    website_url_list = ['http://azzurrabelli.it', 'http://www.thepuffcuff.com', 'http://zhenqingcosmetics.com/', 'https://purebrazilian.com/',\
        'http://www.pyramid-usa.com', 'https://pyurvana.com', 'http://www.hollyren.com', 'http://www.ibeautyac.com', \
        'http://www.isabella-lashes.com', 'http://www.lashnew.com', 'http://www.worldbeautyeyelashes.com ']
    
    run = Run('./')
    run.run("cosmoprof.csv")
    # csv_mapping_list = run.get_csv("cosmoprof.csv")
    
    # email_list = []
    # for row in tqdm(csv_mapping_list, desc='Get Email'):
    #     sns_list = ast.literal_eval(row['sns'])
    #     if sns_list[0] != '':
    #         email = run.run_facebook(sns_list[0])
    #     else:
    #         email = run.run_one(row['website'])
    #     email_list.append(email)
            
    # run.save_data("cosmoprof.csv", email_list)
    
    # for website_url in website_url_list:
    #     result = run.run_one(website_url)
    #     print(result)
