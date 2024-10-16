from hummingbot.strategy.strategy_base import StrategyBase
from hummingbot.strategy.market_trading_pair_tuple import MarketTradingPairTuple
from hummingbot.connector.exchange.paper_trade import PaperTradeExchange
from hummingbot.core.data_type.common import OrderType, TradeType
from hummingbot.core.event.events import OrderFilledEvent
from hummingbot.indicator.simple_moving_average import SimpleMovingAverage

# Global variables
trading_pair = "BTC-USDT"
exchange = "binance"
fast_ma_period = 10
slow_ma_period = 20

class CrossOverStrategy(StrategyBase):
    def __init__(self,
                 market_info: MarketTradingPairTuple,
                 fast_ma_period: int = fast_ma_period,
                 slow_ma_period: int = slow_ma_period):
        super().__init__()
        self._market_info = market_info
        self._fast_ma = SimpleMovingAverage(fast_ma_period)
        self._slow_ma = SimpleMovingAverage(slow_ma_period)
        self._last_trade_side = None

    def on_tick(self):
        # Get the latest price
        current_price = self._market_info.get_mid_price()

        # Update moving averages
        self._fast_ma.update(current_price)
        self._slow_ma.update(current_price)

        if self._fast_ma.ready() and self._slow_ma.ready():
            # Check for crossover conditions
            if self._fast_ma.avg > self._slow_ma.avg and self._last_trade_side != "BUY":
                # Fast MA crosses above slow MA, buy signal
                self.buy_with_specific_market(
                    self._market_info,
                    amount=0.01,  # Replace with your desired amount
                    order_type=OrderType.MARKET
                )
                self._last_trade_side = "BUY"

            elif self._fast_ma.avg < self._slow_ma.avg and self._last_trade_side != "SELL":
                # Fast MA crosses below slow MA, sell signal
                self.sell_with_specific_market(
                    self._market_info,
                    amount=0.01,  # Replace with your desired amount
                    order_type=OrderType.MARKET
                )
                self._last_trade_side = "SELL"


def start(self):
    try:
        # Connect to the exchange
        exchange = PaperTradeExchange(exchange_name="binance")
        exchange.connect()

        # Initialize the strategy
        market_info = MarketTradingPairTuple(exchange, trading_pair, "BTC", "USDT")
        strategy = CrossOverStrategy(market_info)

        # Add the strategy to the bot
        self.add_markets([exchange])
        self.strategies.append(strategy)

    except Exception as e:
        self.logger().error(str(e), exc_info=True)


# This is how you would run the script in Hummingbot
# start --script cross_over_strategy.py --config cross_over_strategy.yml