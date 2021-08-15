import backtrader as bt

class DonchianChannelsIndicator(bt.Indicator):
    '''Donchian channel.'''

    alias = ('DCH', 'DonchianChannel',)

    lines = ('dcm', 'dch', 'dcl',)  # dc middle, dc high, dc low

    params = (
        ('period', 20), # lookback period
    )

    plotinfo = dict(subplot=False)  # plot along with data
    plotlines = dict(
        dcm=dict(ls='--'),  # dashed line
        dch=dict(_samecolor=True),  # use same color as prev line (dcm)
        dcl=dict(_samecolor=True),  # use same color as prev line (dch)
    )

    def __init__(self):
        super().__init__()
        self.addminperiod(self.params.period + 1)
        self.lines.dch = bt.indicators.Highest(self.data.high(-1), period=self.params.period)
        self.lines.dcl = bt.indicators.Lowest(self.data.low(-1), period=self.params.period)
        self.lines.dcm = (self.lines.dch + self.lines.dcl) / 2.0  # avg of the above