import requests
from jobs import calculate_performance_job, update_stocks_job
from dump_stocks import creat_allocation,update_allocation
from pprint import pprint
import yfinance as yf
from datetime import datetime
from update_last import get_last, get_last_index, update
from dump_stocks import calculate_performance_fixed,test
import investpy as ip
import yahooquery as yq

def update_indexs_job():
    print('update_indexs_job start The time is: %s' % datetime.now())
    start= datetime.now()

    symbs=['^FCHI','^GSPC']
    
    for s in symbs:
        get_last_index(s)
    end= datetime.now() -start
    print('update_stocks_job excuted in:'+str(end))


def isin2stockprice(isin):
    
    company_name = ip.stocks.search_stocks(by='isin', value='FR0000053381')
    company_name = company_name["name"][0].split(' ')[0]
    symbol = yq.search(company_name)["quotes"][0]["symbol"]
    print(symbol)


if __name__ == '__main__':
    # update_stocks_job()
    # calculate_performance_job()
    # update_indexs_job()
    # calculate_performance_fixed()
    test()

    # data=yf.Ticker('MSFT').get_info()['logo_url']
    # print(data)

    # update_stocks_job()

    # update_indexs_job()

    # isin2stockprice('FR0000053381')


# get_last('SCHD')
# update_allocation('us dividends')

