# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy, IntParameter
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class Best(IStrategy):

    INTERFACE_VERSION: int = 3
    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "60":  0.01,
        "30":  0.03,
        "20":  0.04,
        "0":  0.05
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.10

    # Optimal timeframe for the strategy
    timeframe = "1h"

    # trailing stoploss
    trailing_stop = False
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02

    # run "populate_indicators" only for new candle
    process_only_new_candles = True

    # Experimental settings (configuration will overide these if set)
    use_exit_signal = True
    exit_profit_only = True
    ignore_roi_if_entry_signal = False

    # Optional order type mapping
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    # Hyperoptable EMA periods (tuned for 1h timeframe)
    buy_ema_fast = IntParameter(5, 30, default=12, space="buy")
    buy_ema_slow = IntParameter(20, 100, default=50, space="buy")
    sell_ema_fast = IntParameter(10, 40, default=20, space="sell")
    sell_ema_slow = IntParameter(40, 200, default=100, space="sell")

    # Ensure enough candles for the slowest EMA
    startup_candle_count = 200

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """

        buy_fast = self.buy_ema_fast.value
        buy_slow = self.buy_ema_slow.value
        sell_fast = self.sell_ema_fast.value
        sell_slow = self.sell_ema_slow.value

        # Use stable column names so hyperopt doesn't hit missing columns
        dataframe['ema_buy_fast'] = ta.EMA(dataframe, timeperiod=buy_fast)
        dataframe['ema_buy_slow'] = ta.EMA(dataframe, timeperiod=buy_slow)
        dataframe['ema_sell_fast'] = ta.EMA(dataframe, timeperiod=sell_fast)
        dataframe['ema_sell_slow'] = ta.EMA(dataframe, timeperiod=sell_slow)

        heikinashi = qtpylib.heikinashi(dataframe)
        dataframe['ha_open'] = heikinashi['open']
        dataframe['ha_close'] = heikinashi['close']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        if 'ema_buy_fast' not in dataframe.columns or 'ema_buy_slow' not in dataframe.columns:
            dataframe['ema_buy_fast'] = ta.EMA(dataframe, timeperiod=self.buy_ema_fast.value)
            dataframe['ema_buy_slow'] = ta.EMA(dataframe, timeperiod=self.buy_ema_slow.value)
        ema_fast = dataframe['ema_buy_fast']
        ema_slow = dataframe['ema_buy_slow']

        dataframe.loc[
            (
                qtpylib.crossed_above(ema_fast, ema_slow) &
                (dataframe['ha_close'] > ema_fast) &
                (dataframe['ha_open'] < dataframe['ha_close'])  # green bar
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        if 'ema_sell_fast' not in dataframe.columns or 'ema_sell_slow' not in dataframe.columns:
            dataframe['ema_sell_fast'] = ta.EMA(dataframe, timeperiod=self.sell_ema_fast.value)
            dataframe['ema_sell_slow'] = ta.EMA(dataframe, timeperiod=self.sell_ema_slow.value)
        ema_fast = dataframe['ema_sell_fast']
        ema_slow = dataframe['ema_sell_slow']

        dataframe.loc[
            (
                qtpylib.crossed_below(ema_fast, ema_slow) &
                (dataframe['ha_close'] < ema_fast) &
                (dataframe['ha_open'] > dataframe['ha_close'])  # red bar
            ),
            'exit_long'] = 1
        return dataframe
