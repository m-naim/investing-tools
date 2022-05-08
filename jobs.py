from datetime import datetime

import pytz
from dump_stocks import calculate_performance
from config import db
from update_last import get_portfolios_symbs, update 
import requests
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()
timezone=pytz.timezone('Europe/Paris')

# interval example
# @scheduler.task('cron', id='do_job_1',day_of_week='mon-fri', hour="9-23/1")
def calculate_performance_job():
    start= datetime.now()
    print('calculate_performance_job start The time is: %s' %start)
    portfolios=db.portfolios.find({},{"name":1, "_id":0})
    for pf in portfolios:
        print(pf)
        calculate_performance(pf['name'])
    end= datetime.now() -start
    print('update_stocks_job excuted in:'+str(end))


# @scheduler.task('cron', id='do_job_2',day_of_week='mon-fri', hour="9-23/1")
def update_stocks_job():
    print('update_stocks_job start The time is: %s' % datetime.now())
    start= datetime.now()
    portfolios=db.portfolios.find({},{"name":1, "_id":0})
    symbs=[]
    for pf in portfolios:
        print(pf)
        symbs += get_portfolios_symbs(pf['name'])
    symbs= set(symbs)
    print(symbs)
    update(symbs)
    end= datetime.now() -start
    print('update_stocks_job excuted in:'+str(end))


# @scheduler.task('cron', id='up', minute="*/1")
def wakeup():
    print('wakeup start The time is: %s' % datetime.now())
    result=requests.get("https://karius-api.herokuapp.com/health")
    print(result.content)

if __name__ == '__main__':
    print("program started")
    scheduler.add_job(calculate_performance_job, 'cron', day_of_week='mon-fri', hour="9-23/1", timezone='Europe/Paris')
    scheduler.add_job(update_stocks_job, 'cron', day_of_week='mon-fri', hour="9-23/1", timezone='Europe/Paris')
    scheduler.add_job(wakeup, 'cron', minute="*/1", timezone='Europe/Paris')
    scheduler.start()