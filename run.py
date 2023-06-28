from src.combinated_crawler import Crawler
from src.db_connecter import DB
import traceback
import time
from apscheduler.schedulers.blocking import BlockingScheduler


scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour='23', minute='18', id='crawler')
def runner():
    print("--------")
    print("starting crawler")
    print("--------\n")

    crawler = Crawler()
    db = DB()
    website_table = db.read_url()

    for i in range(len(website_table)):
        id = website_table.loc[i, 'id']
        url = website_table.loc[i, 'url']
        headers = website_table.loc[i, 'headers']
        func_name = "crawl_"+str(id)
        website_crawler = getattr(crawler, func_name)

        try:
            website_crawler(id, url, headers)
        except:
            try:
                crawler.__init__()
                website_crawler(id, url, headers)
            except:
                err_msg = traceback.format_exc()
                print("\n\n============error", str(id), "website crawling")
                print(err_msg)
                print("============\n\n")
                continue
            else:
                print("finished crawling for " +str(id)+ " website\n")           
        else:
            print("finished crawling for " +str(id)+ " website\n")

        try:
            db.insert_data(id)
        except:
            try:
                db.__init__()
                db.insert_data(id)
            except:
                err_msg = traceback.format_exc()
                print("\n\n============error", str(id), "website data inserting")
                print(err_msg)
                print("============\n\n")
                continue           
    
    print("--------")
    print("finishing crawler")
    print("--------\n")

scheduler.start()
