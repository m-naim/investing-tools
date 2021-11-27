import quantstats as qs
import pandas as pd
import yfinance as _yf
from yfinance import ticker
import portfolio
import util
import os
# extend pandas functionality with metrics, etc.
qs.extend_pandas()


# portfolio={
#     "MSFT":0.4,
#     "SU.PA":0.3,
#     "TTE.PA":0.1,
#     "NXI.PA":0.1,
#     "VCT.PA":0.1
# }
 
# retuns_data= qs.utils.make_index(portfolio,period="1y")

# dividend_portfolio= {
#     "MSFT": 0.07,
#     "AAPL": 0.14,
#     "IGV":  0.07,
#     "DIS":  0.0902,
#     "COST": 0.0528,
#     "HD":   0.0396,
#     "NKE": 0.0154,
#     "CMCSA":0.0132,
#     "TGT":  0.0088,
#     "SCHD": 0.07,
#     "JPI":  0.07,
#     "VICI": 0.07,
#     "STOR": 0.0322,
#     "MGP":  0.0154,
#     "SPG":  0.0126,
#     "O":    0.0098,
#     "JPM":  0.0858,
#     "MA":   0.0195,
#     "V":    0.0169,
#     "TROW": 0.0078,
#     "ABBV": 0.021,
#     "JNJ":  0.009,
#     "D":    0.0225,
#     "NEE":  0.0075,
#     "TXRH": 0.03,
#     "VZ":   0.01
# }
# capital=1000
# dividend_portfolio_df=pd.DataFrame(dividend_portfolio.items(),columns=['ticker','weigth'])
# dividend_portfolio_df['last']= dividend_portfolio_df['ticker'].apply(lambda t: _yf.Ticker(t).history('1d')['Close'])
# dividend_portfolio_df['shares number']= capital*dividend_portfolio_df['weigth']/dividend_portfolio_df['last']

filename= os.path.join("portfolios","us_dividend_portfolio.xlsx")
# dividend_portfolio_df.to_excel(filename)

retuns_data=portfolio.portfolio_from_degiro_transactions()
# retuns_data.to_excel('data.xlsx')

# for c in retuns_data.columns.values:
#     retuns_data[c] = (1 + retuns_data[c]).cumprod()
# util.plot_graph_multiple(retuns_data,'portfolio')

retuns_data= retuns_data.dropna()
# retuns_data['sum']= retuns_data.sum(axis=1)
# retuns_data['pf']=qs.utils.make_portfolio(retuns_data['sum'],460)
# retuns_data['cum'] = (1 + retuns_data['sum']).cumprod()
# print(retuns_data)

# util.plot_graph(retuns_data['cum'],'portfolio')
# retuns_data = (1 + retuns_data).cumprod()
# or using extend_pandas() :)

# dividend_portfolio_df= pd.read_excel(filename)
# del dividend_portfolio_df['weigth']
# del dividend_portfolio_df['last']
# del dividend_portfolio_df['shares number']
# del dividend_portfolio_df['value']
# del dividend_portfolio_df['Unnamed: 0']

# dividend_portfolio_df=dividend_portfolio_df.drop(dividend_portfolio_df.index[-1],axis=0)
# dividend_portfolio_df= dividend_portfolio_df[dividend_portfolio_df["nw"]>0]
# dividend_portfolio= dividend_portfolio_df.set_index('ticker').T.to_dict('records')[0]

# retuns_data=qs.utils.make_index(dividend_portfolio,True,"10y")
qs.reports.html(retuns_data, "SPY", output="hello.html")

# to csv
# del dividend_portfolio_df['nw']
# dividend_portfolio_df['Weight']=dividend_portfolio_df['Weight'].apply(lambda w: str(w*100)+'%')
# dividend_portfolio_df=dividend_portfolio_df.set_index('Symbol')
# dividend_portfolio_df.to_csv('pf.csv')