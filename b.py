from hummingbot.strategy.strategy_base import StrategyBase
from hummingbot.strategy.market_trading_pair_tuple import MarketTradingPairTuple
from hummingbot.connector.exchange.paper_trade import PaperTradeExchange
from hummingbot.connector.exchange_base import ExchangeBase
from hummingbot.core.data_type.common import OrderType
from hummingbot.core.event.events import OrderFilledEvent
from hummingbot.core.data_type.order_candidate import OrderCandidate
from hummingbot.indicator.simple_moving_average import SimpleMovingAverage

# Import the Decimal class for precise decimal calculations
from decimal import Decimal


class MaCrossStrategy(StrategyBase):
    # Define the strategy parameters
    fast_ma_period: int = 5
    slow_ma_period: int = 20
    order_amount: Decimal = Decimal("0.01")
    trading_pair: str = "ETH-USDT"
    exchange_name: str = "binance"

    # Initialize the strategy
    def __init__(self):
        super().__init__()
        self.fast_ma = SimpleMovingAverage(self.fast_ma_period)
        self.slow_ma = SimpleMovingAverage(self.slow_ma_period)
        self.market_info: MarketTradingPairTuple = MarketTradingPairTuple(
            self.exchange, self.trading_pair
        )
        self.in_position = False

    # Called when the strategy is started
    def start(self, clock: 'Clock', timestamp: float):
        super().start(clock, timestamp)
        print(f"Starting MA Cross strategy with {self.fast_ma_period}/{self.slow_ma_period} MA periods.")

    # Called on each tick (default is 1 second)
    def tick(self, timestamp: float):
        # Get the latest price
        price = self.market_info.get_mid_price()

        # Update the moving averages
        self.fast_ma.update(price)
        self.slow_ma.update(price)

        # Check if enough candles have been collected
        if self.fast_ma.ready() and self.slow_ma.ready():
            # If not in position and fast MA crosses above slow MA, buy
            if not self.in_position and self.fast_ma.avg > self.slow_ma.avg:
                self.buy_order_candidate = OrderCandidate(
                    trading_pair=self.trading_pair,
                    is_maker=False,
                    order_type=OrderType.MARKET,
                    order_side=TradeType.BUY,
                    amount=self.order_amount,
                )
                self.place_order(self.buy_order_candidate)
                self.in_position = True
                print(f"Bought {self.order_amount} {self.trading_pair} at {price}")

            # If in position and fast MA crosses below slow MA, sell
            elif self.in_position and self.fast_ma.avg < self.slow_ma.avg:
                self.sell_order_candidate = OrderCandidate(
                    trading_pair=self.trading_pair,
                    is_maker=False,
                    order_type=OrderType.MARKET,
                    order_side=TradeType.SELL,
                    amount=self.order_amount,
                )
                self.place_order(self.sell_order_candidate)
                self.in_position = False
                print(f"Sold {self.order_amount} {self.trading_pair} at {price}")

    # Called when an order is filled
    def did_fill_order(self, event: OrderFilledEvent):
        order_id = event.order_id
        market_info = event.trading_pair
        order_type = event.trade_type
        amount = event.amount
        price = event.price

        # Log the filled order
        print(f"Order filled: {order_id} - {market_info} - {order_type} - {amount} - {price}")


# Define the exchange and trading pair
exchange = PaperTradeExchange(ExchangeBase.PAPER_TRADE_MODE)
trading_pair = "ETH-USDT"

# Create and start the strategy
strategy = MaCrossStrategy()
strategy.exchange = exchange
strategy.trading_pair = trading_pair
strategy.start(clock=Clock(), timestamp=time.time())