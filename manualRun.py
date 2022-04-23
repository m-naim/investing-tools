from pkgutil import ImpImporter

from run import calculate_performance_job, update_stocks_job
from dump_stocks import creat_allocation,update_allocation
from pprint import pprint
import yfinance as yf

from update_last import get_last, update

# calculate_performance_job()
# get_last('SCHD')
update_allocation('us dividends')
# if __name__ == '__main__':
#     update_stocks_job()
#     ticker=yf.Ticker('SWP.PA')
#     pprint(ticker.info)