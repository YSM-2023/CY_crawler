from facebook import FacebookCrawler 
from googling import Googling 

class Run:
    
    def __init__(self, save_path):
        self.save_path = save_path
        
    def run_one(self, website_url):
        googling = Googling(website_url)
        print(website_url)
        
        facebook_page_url = googling.run_one()

        if facebook_page_url != '':
            fc = FacebookCrawler('')
            icon_list = fc.run_one(facebook_page_url)
            print(facebook_page_url)
            return icon_list
        return 'Fail'
        
    
    
if __name__ == '__main__':
    
    website_url_list = ['http://azzurrabelli.it', 'http://www.thepuffcuff.com', 'http://zhenqingcosmetics.com/', 'https://purebrazilian.com/',\
        'http://www.pyramid-usa.com', 'https://pyurvana.com', 'http://www.hollyren.com', 'http://www.ibeautyac.com', \
        'http://www.isabella-lashes.com', 'http://www.lashnew.com', 'http://www.worldbeautyeyelashes.com ']
    
    run = Run('')
    
    for website_url in website_url_list:
        result = run.run_one(website_url)
        print(result)
