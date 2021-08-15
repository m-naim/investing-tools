import backtrader as bt
from backtrader import sizer
from .donchian_channels import DonchianChannelsIndicator

# Create a subclass of Strategy to define the indicators and logic

class ClenowTrendFollowingStrategy(bt.Strategy):
    """The trend following strategy from the book "Following the trend" by Andreas Clenow."""
    alias = ('ClenowTrendFollowing',)

    params = (
        ('trend_filter_fast_period', 50),
        ('trend_filter_slow_period', 100),
        ('fast_donchian_channel_period', 25),
        ('slow_donchian_channel_period', 50),
        ('trailing_stop_atr_period', 100),
        ('trailing_stop_atr_count', 3),
        ('risk_factor', 0.002)
    )

    def __init__(self):
        self.trend_filter_fast = bt.indicators.EMA(period=self.params.trend_filter_fast_period)
        self.trend_filter_slow = bt.indicators.EMA(period=self.params.trend_filter_slow_period)
        self.dc_fast = DonchianChannelsIndicator(period=self.params.fast_donchian_channel_period)
        self.dc_slow = DonchianChannelsIndicator(period=self.params.slow_donchian_channel_period)
        self.atr = bt.indicators.ATR(period=self.params.trailing_stop_atr_period)
        self.order = None  # the pending order
        # For trailing stop loss
        self.sl_order = None # trailing stop order
        self.sl_price = None
        self.max_price = None # track the highest price after opening long positions
        self.min_price = None # track the lowest price after opening short positions

    def next(self):
        # self.dc_slow.dcl <= self.dc_fast.dcl <= self.dc_fast.dch <= self.dc_slow.dch
        assert self.dc_slow.dcl <= self.dc_fast.dcl
        assert self.dc_fast.dcl <= self.dc_fast.dch
        assert self.dc_fast.dch <= self.dc_slow.dch

        sizer = self.broker.get_cash() / self.datas[0].open

        if not self.position: # Entry rules
            assert self.position.size == 0
            
            # Position size rule
            max_loss = self.broker.get_cash() * self.p.risk_factor # cash you afford to loss
            position_size = max_loss / self.atr[0]

            if self.data.close > self.dc_slow.dch:
                if self.trend_filter_fast > self.trend_filter_slow: # trend filter
                    if self.order:
                        self.broker.cancel(self.order)
                    else:
                        # Entry rule 1
                        self.order = self.buy(price=self.data.close[0], size=sizer, exectype=bt.Order.Limit) 
                        self.max_price = self.data.close[0]
            elif self.data.close < self.dc_slow.dcl:
                if self.trend_filter_fast  < self.trend_filter_slow: # trend filter
                    if self.order:
                        self.broker.cancel(self.order)
                    else:
                        # Entry rule 2
                        self.order = self.sell(price=self.data.close[0], size=sizer, exectype=bt.Order.Limit) 
                        self.min_price = self.data.close[0]
        else:
            assert self.position.size
            # assert self.order is None

            # Exit rules
            if self.position.size > 0:
                # Exit rule 1
                if self.data.close < self.dc_fast.dcl:
                    self.order = self.order_target_value(target=0.0, exectype=bt.Order.Limit, price=self.data.close[0])
                    return
            else:
                # Exit rule 2
                if self.data.close > self.dc_fast.dch:
                    self.order = self.order_target_value(target=0.0, exectype=bt.Order.Limit, price=self.data.close[0])
                    return

            # Trailing stop loss
            trail_amount = self.atr[0] * self.p.trailing_stop_atr_count
            if self.position.size > 0:
                self.max_price = self.data.close[0] if self.max_price is None else max(self.max_price, self.data.close[0])
                if self.sl_price is None or self.sl_price < self.max_price - trail_amount:
                    self.sl_price = self.max_price - trail_amount # increase trailing price
                    if self.sl_order:
                        self.broker.cancel(self.sl_order)
                    else:
                        self.sl_order = self.order_target_value(target=0.0, exectype=bt.Order.Stop, price=self.sl_price)
            elif self.position.size < 0:
                self.min_price = self.data.close[0] if self.min_price is None else min(self.min_price, self.data.close[0])
                if self.sl_price is None or self.sl_price > self.min_price + trail_amount:
                    self.sl_price = self.min_price + trail_amount # decrease trailing price
                    if self.sl_order:
                        self.broker.cancel(self.sl_order)
                    else:
                        self.sl_order = self.order_target_value(target=0.0, exectype=bt.Order.Stop, price=self.sl_price)

    def notify_order(self, order):
        if order.status in [order.Created, order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # print logs here

        # Write down: no pending order
        if order.exectype == bt.Order.Stop:
            self.sl_order = None
        else:
            self.order = None