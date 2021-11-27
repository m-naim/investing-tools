import pandas as pd
from importlib.machinery import SourceFileLoader
from datetime import datetime
import yfinance

db = SourceFileLoader('*', '../config.py').load_module().db
stocks_dictionary_file=pd.read_excel("stocksDictionary.xlsx")
stocks_dictionary=stocks_dictionary_file.set_index('Names')
stocks_dictionary= stocks_dictionary[['Symboles']]
dict=stocks_dictionary.T.to_dict('records')[0]

def print_trans():
    transactions_file=pd.read_csv("transactions(1).csv")
    print(transactions_file.head(20))

def portfolio_from_degiro_transactions():
    transactions_file=pd.read_csv("transactions(1).csv")
    transactions= transactions_file[['Date','Quantité']]
    transactions['price']= transactions_file.loc[:, ('Montant')]*-1
    transactions = transactions.rename(columns={'Date':'date','Quantité':'qty'})
    transactions['date']= transactions['date'].apply(lambda d: datetime.strptime(d,'%d-%m-%Y')) 
    transactions['symbol']= transactions_file['Produit'].apply(lambda x: dict[x])
    transactions=transactions.to_dict('records')
    return transactions

def compute_allocation(trns):
    df = pd.DataFrame(trns)
    print(df[df['symbol']=='DBG.PA'])
    allocation= df.groupby(['symbol']).sum()
    allocation= allocation[allocation['qty'] > 0] 
    allocation=allocation.reset_index()
    allocation['name']= allocation['symbol'].map(stocks_dictionary_file.set_index('Symboles')['Names'])
    allocation['bpe']= allocation['price']/allocation['qty']
    allocation['last']= allocation['symbol'].apply(lambda s: yfinance.Ticker(s).history(period="1d").iloc[0]['Close'])
    allocation['total_value']= allocation['last']*allocation['qty']
    allocation['weight']= round(allocation['total_value']/allocation['total_value'].sum(),3)
    allocation= allocation.rename(columns={'price':'value'})
    allocation=allocation.to_dict('records')
    return allocation

trns=portfolio_from_degiro_transactions()
alloc=compute_allocation(trns)

try:
    collection = db.portfolios.find_one({'name':"current"})
    collection['allocation']= alloc
    collection['transactions']=trns
    db.portfolios.update_one({'name':"current"},{'$set':collection})

except Exception as e:
    print(e)