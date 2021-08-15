import pandas as pd
import quantstats as qs
import scraper

equities= pd.read_excel('equities_sharp_ratio.xlsx')
del equities['Unnamed: 0']
equities_returns=pd.DataFrame(columns= equities['Symbol'].tolist())
# for s in equities['Symbol'].tolist():
#     equities_returns[s]= qs.utils.download_returns(s,'5y') 

# equities['Sortino ratio']= equities['Symbol'].apply(lambda s: qs.stats.sortino(equities_returns[s]))
# equities['Common Sense Ratio']= equities['Symbol'].apply(lambda s: qs.stats.common_sense_ratio(equities_returns[s]))
# equities['calmar']= equities['Symbol'].apply(lambda s: qs.stats.calmar(equities_returns[s]))
# equities['kelly criterion']= equities['Symbol'].apply(lambda s: qs.stats.kelly_criterion(equities_returns[s])) 
# equities['expected return']= equities['Symbol'].apply(lambda s: qs.stats.expected_return(equities_returns[s]),'month') 


equities['peg']= equities['Symbol'].apply(lambda s: scraper.get_peg(s)) 

equities.to_excel("equities_sharp_ratio.xlsx")