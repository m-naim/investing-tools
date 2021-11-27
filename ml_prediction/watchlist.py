import pandas as pd 

watchlist= pd.read_excel('watchlist.xlsx')['tickers'].tolist()

print(watchlist)