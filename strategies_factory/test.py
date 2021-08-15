import backtrader as bt
import yfinance as _yf
from strategies.trend_folowing import ClenowTrendFollowingStrategy

from typing import Dict, List, Tuple, Union

import os
import multiprocessing
from tqdm.contrib.concurrent import process_map 
import backtrader as bt
import pandas as pd


# Create a subclass of Strategy to define the indicators and logic
import quantstats as qs

data_df =  _yf.Ticker('MSFT').history('2y')
data_feed= bt.feeds.PandasData(dataname=data_df)

def run_strategy(
    params: Dict[str, Union[float, int]] = {
        'trend_filter_fast_period': 50,
        'trend_filter_slow_period': 100,
        'fast_donchian_channel_period': 25,
        'slow_donchian_channel_period': 50,
        'trailing_stop_atr_period': 100,
        'trailing_stop_atr_count': 3,
        'risk_factor': 0.002
    }
):
    cerebro = bt.Cerebro(maxcpus=1)
    cerebro.addstrategy(ClenowTrendFollowingStrategy, 
                        trend_filter_fast_period=params['trend_filter_fast_period'],
                        trend_filter_slow_period = params['trend_filter_slow_period'],
                        fast_donchian_channel_period = params['fast_donchian_channel_period'],
                        slow_donchian_channel_period = params['slow_donchian_channel_period'],
                        trailing_stop_atr_period = params['trailing_stop_atr_period'],
                        trailing_stop_atr_count = params['trailing_stop_atr_count'],
                        risk_factor = params['risk_factor'])
   
    cerebro.adddata(data_feed)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Days, compression=1, factor=365, annualize=True)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Days, compression=1, tann=365)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, data=data_feed, _name='buyandhold')
    INITIAL_CASH= cerebro.broker.get_cash()
    results = cerebro.run()
    assert len(results) == 1
    stats = {
        # 'PnL': list(results[0].analyzers.timereturn.get_analysis().values())[0],
        'PnL': cerebro.broker.getvalue()/INITIAL_CASH-1,
        'BnH': list(results[0].analyzers.buyandhold.get_analysis().values())[0],
        'Sharpe_Ratio': results[0].analyzers.sharperatio.get_analysis()['sharperatio'],
        'CARG': results[0].analyzers.returns.get_analysis()['ravg'],
        'Max_Drawdown': results[0].analyzers.drawdown.get_analysis().max.drawdown/100,
        'num_trades': results[0].analyzers.ta.get_analysis().total.total,
    }
    return {**params, **stats}

def grid_search()->pd.DataFrame:
    params_list = []
    
    for fast_donchian_channel_period in range(30, 40):
        for m1 in range(2, 4):
            for m2 in range(2, 4):
                for atr_count in range(3, 6):
                    params = {
                    'trend_filter_fast_period': fast_donchian_channel_period * m1,
                    'trend_filter_slow_period': fast_donchian_channel_period * m1 * m2,
                    'fast_donchian_channel_period': fast_donchian_channel_period,
                    'slow_donchian_channel_period': fast_donchian_channel_period * m1,
                    'trailing_stop_atr_period': fast_donchian_channel_period * m1 * m2,
                    'trailing_stop_atr_count': atr_count,
                    'risk_factor': 0.002
                    }
                    params_list.append(params)



    
    stats = map(run_strategy, params_list)

    # stats = process_map(run_strategy, params_list, max_workers=os.cpu_count())
    
    df = pd.DataFrame(stats)
    df.sort_values('Sharpe_Ratio', ascending=False, inplace=True)
    return df

def demo():
    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
    # Create a data feed

    cerebro.adddata(data_feed)  # Add the data feed

    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    params= {
        'trend_filter_fast_period': 78,
        'trend_filter_slow_period': 156,
        'fast_donchian_channel_period': 78,
        'slow_donchian_channel_period': 156,
        'trailing_stop_atr_period': 156,
        'trailing_stop_atr_count': 5,
        'risk_factor': 1
    }
    cerebro.addstrategy(ClenowTrendFollowingStrategy,
        trend_filter_fast_period=params['trend_filter_fast_period'],
        trend_filter_slow_period = params['trend_filter_slow_period'],
        fast_donchian_channel_period = params['fast_donchian_channel_period'],
        slow_donchian_channel_period = params['slow_donchian_channel_period'],
        trailing_stop_atr_period = params['trailing_stop_atr_period'],
        trailing_stop_atr_count = params['trailing_stop_atr_count'],
        risk_factor = params['risk_factor']
    )  # Add the trading strategy
    res= cerebro.run()  # run it all
    # Analyzer
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    thestrats = cerebro.run()
    thestrat = thestrats[0]

    portfolio_stats = thestrat.analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
    returns.index = returns.index.tz_convert(None)
    cerebro.plot()

    qs.reports.html(returns,'MSFT',output='stats.html', title='strat_stats.html')

demo()