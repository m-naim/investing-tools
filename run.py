from datetime import datetime
from multiprocessing.connection import wait
from unittest import result
from dump_stocks import calculate_performance
from server import app
from flask_apscheduler import APScheduler
from config import db
from update_last import get_portfolios_symbs, update 
import requests
class Config:
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()

# interval example
@scheduler.task('cron', id='do_job_1',day_of_week='mon-fri', hour="9-23/1")
def calculate_performance_job():
    start= datetime.now()
    print('calculate_performance_job start The time is: %s' %start)
    portfolios=db.portfolios.find({},{"name":1, "_id":0})
    for pf in portfolios:
        print(pf)
        calculate_performance(pf['name'])
    end= datetime.now() -start
    print('update_stocks_job excuted in:'+str(end))


@scheduler.task('cron', id='do_job_2',day_of_week='mon-fri', hour="9-23/1")
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


@scheduler.task('cron', id='up', minute="*/10")
def wakeup():
    print('wakeup start The time is: %s' % datetime.now())
    result=requests.get("https://karius-api.herokuapp.com/health")
    print(result)

if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True,use_reloader=True, port=5000, threaded=True)
