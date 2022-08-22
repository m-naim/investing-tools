from pkgutil import ImpImporter

from jobs import calculate_performance_job, update_stocks_job
from dump_stocks import creat_allocation,update_allocation
from pprint import pprint
import yfinance as yf
from datetime import datetime
from update_last import get_last, get_last_index, update

def update_indexs_job():
    print('update_indexs_job start The time is: %s' % datetime.now())
    start= datetime.now()

    symbs=['^FCHI','^GSPC']
    
    for s in symbs:
        get_last_index(s)
    end= datetime.now() -start
    print('update_stocks_job excuted in:'+str(end))


if __name__ == '__main__':
    update_stocks_job()
    calculate_performance_job()
    update_indexs_job()


# get_last('SCHD')
# update_allocation('us dividends')

