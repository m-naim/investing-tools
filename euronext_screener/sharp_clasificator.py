import pandas as pd
import quantstats as qs
import scraper
from importlib.machinery import SourceFileLoader
from pprint import pprint
import time
import multiprocessing.pool as mp

def get_stats(s):
    try:
        equitie={"symbol":s}
        returns= qs.utils.download_returns(s,'5y') 
        equitie['Sortino ratio']= qs.stats.sortino(returns)
        equitie['Common Sense Ratio']= qs.stats.common_sense_ratio(returns)
        equitie['calmar']= qs.stats.calmar(returns)
        equitie['kelly criterion']= qs.stats.kelly_criterion(returns) 
        equitie['expected return']= qs.stats.expected_return(returns,'month') 
        equitie['peg']= scraper.get_peg(s)
        return equitie
    except Exception as e:
        print(e)
        return



if __name__=="__main__":
    db = SourceFileLoader('*', '../config.py').load_module().db
    equities= pd.read_excel('equities_sharp_ratio.xlsx')
    del equities['Unnamed: 0']
    p=mp.Pool(8)
    start = time.time()
    # equities_returns=pd.DataFrame(columns= equities['Symbol'].tolist())
    symbols= equities['Symbol'].tolist()
    equities=p.map(get_stats,symbols)
    p.close()
    p.join()

    # equities.to_excel("equities_sharp_ratio.xlsx")
    # equities.fillna('null',inplace=True)
    # documents=equities.T.to_dict().values()
    equities= list(filter(lambda x: x is not None, equities))
    db.stocks.insert_many(equities)
    end = time.time()
    print("The time of execution of above program is :", end-start)