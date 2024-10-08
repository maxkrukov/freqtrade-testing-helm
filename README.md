# Freqtrade Testing Helm Chart (job)

The **freqtrade-testing-helm** chart enables you to deploy [Freqtrade](https://www.freqtrade.io/), an open-source cryptocurrency trading bot, in a Kubernetes environment. It supports backtesting with historical data, hyperoptimization to fine-tune strategies, and data downloading for accurate testing and simulations.

## What is Freqtrade?

Freqtrade is a highly flexible cryptocurrency trading bot that allows users to automate their trading on exchanges like Binance and Kraken. It enables you to define and run custom strategies, with built-in support for:

- **Backtesting**: Test how your strategies would have performed in the past using historical data.
- **Hyperoptimization**: Automatically adjust and optimize strategy parameters for better results based on historical data.

For a detailed overview of Freqtrade's configuration options, visit the official [Freqtrade Configuration Documentation](https://www.freqtrade.io/en/stable/configuration/).

## Why Use Backtesting, Hyperopt, and Data Download?

### Backtesting

Backtesting simulates the performance of a trading strategy by applying it to historical data. This helps you evaluate how a strategy would have performed in the past without risking real funds. You can assess the profitability, risk, and overall viability of a strategy before deploying it for live trading.

### Hyperopt

Hyperoptimization (Hyperopt) helps you fine-tune the parameters of your trading strategy. Instead of manually adjusting values like stop-loss or ROI thresholds, Hyperopt automatically searches for the optimal combination of parameters that yield the best results, based on your chosen performance metrics (e.g., profit, Sharpe Ratio, drawdown).

### Downloading Historical Data

To run accurate backtests and hyperopt simulations, you need historical market data. This chart includes the ability to download historical data for specific trading pairs and timeframes. This is particularly useful if you're running strategies on specific assets or timeframes not included in the bot’s default setup.

---

## Chart Overview

This Helm chart deploys and manages the Freqtrade bot in a Kubernetes cluster. It supports:

- **Backtesting**: Test your trading strategies using historical data.
- **Hyperopt**: Optimize strategy parameters for improved performance.
- **Data Download**: Download historical market data to ensure accurate backtesting and hyperopt results.
- **Persistent Storage**: Use Persistent Volume Claims (PVC) to store strategies and bot data.

---

## Installation

To install the Freqtrade testing Helm chart, first add the Helm repository:

```bash
helm repo add fretrade-testing https://raw.githubusercontent.com/maxkrukov/freqtrade-testing-helm/refs/heads/main
```

Then upgrade and install the chart using your custom values:

```bash
helm upgrade -i -f custom-values.yaml fretrade-testing/fretrade-testing
```

---

## Freqtrade Configuration

The **freqtrade-testing-helm** chart allows you to fully customize your bot configuration through the `values.yaml` file. Below is an explanation of the key configuration options for Freqtrade.

### General Settings

- **`bot_name`**: Sets the name of your Freqtrade bot, used internally to identify the bot.
- **`max_open_trades`**: Defines the maximum number of trades that can be open at any time, limiting your exposure.
- **`stake_amount`**: The amount to be staked in each trade, set according to your risk tolerance.
- **`stake_currency`**: The currency in which you will stake, such as `USDT` or `BTC`.

### Trading Settings

- **`timeframe`**: Specifies the timeframe for trading (e.g., `5m` for 5-minute candlestick intervals). Different strategies perform better on different timeframes.
- **`tradable_balance_ratio`**: Sets the portion of the total available balance that can be used for trading (e.g., `0.9999`), helping to prevent overexposure.
- **`trading_mode`**: Determines whether the bot is trading in `spot` or `futures` mode, depending on your exchange and risk preferences.
- **`use_exit_signal`**: If set to `true`, the bot will automatically use exit signals to close trades, based on your strategy.

### Position Management (DCA)

- **`position_adjustment_enable`**: Enables Dollar-Cost Averaging (DCA), allowing the bot to adjust position entries in the event of price declines to improve the average buy price.
- **`max_entry_position_adjustment`**: The maximum number of times DCA can be applied to adjust a position.

### Exchange Configuration

- **`exchange.name`**: Defines the exchange the bot will trade on (e.g., `binance`, `kraken`).
- **`exchange.pair_whitelist`**: A list of trading pairs the bot is allowed to trade. Example: `ETH/USDT`. More pairs can be added to expand your trading universe.

### Pricing Strategy

- **`entry_pricing`**: Determines how the bot identifies entry points based on market order book data. You can specify whether to use the order book and set various thresholds for market depth.
- **`exit_pricing`**: Similar to entry pricing but used for determining exit points.

### Resource Management

To control resource allocation for the Freqtrade bot on Kubernetes, you can define resource requests and limits in `values.yaml`. This ensures that your bot operates within defined resource constraints, preventing it from overusing memory or CPU.

```yaml
resources:
  requests:
    memory: "512Mi"  # Minimum memory allocation
    cpu: "500m"  # Minimum CPU allocation
  limits:
    memory: "1Gi"  # Maximum memory allocation
    cpu: "1"  # Maximum CPU limit
```

### Docker Image

The bot is deployed in a Docker container. You can control which Docker image version is used by modifying these parameters:

- **`repository`**: The Docker image repository where the Freqtrade bot is hosted. The default repository is `freqtradeorg/freqtrade`.
- **`tag`**: The version of the Docker image to pull. For example, `"2023.12"`.
- **`pullPolicy`**: Defines when the Docker image should be pulled (`IfNotPresent`, `Always`, etc.).

Example configuration:

```yaml
image:
  repository: freqtradeorg/freqtrade
  tag: "2023.12"
  pullPolicy: IfNotPresent
```

---

## Backtesting, Hyperopt, and Data Download

Backtesting, hyperopt, and data download features allow you to simulate, optimize, and prepare your bot for real-world scenarios using historical data. These features can be configured in `values.yaml`.

### Backtesting

Backtesting helps you validate your strategy by running it against historical data, enabling you to understand how it would have performed in real-world scenarios.

```yaml
testing:
  backtesting:
    enabled: true  # Enable backtesting
    days: 30  # Number of historical days to use
    breakdown: "day"  # Granularity of backtest results (day or month)
    fee: 0.0005  # Trading fee applied during backtesting
```

### Hyperopt

Hyperopt is a tool that optimizes your strategy's parameters by finding the best combinations of settings such as stop-loss, ROI thresholds, etc., based on historical data.

```yaml
testing:
  hyperopt:
    enabled: true
    offset: 0 # Period x days ago
    days: 30  # Number of days of historical data used for optimization
    hyperoptStrategy: "SharpeHyperOptLossDaily"  # The optimization strategy to use
    spaces:
      - roi  # Optimize ROI parameters
      - stoploss  # Optimize stoploss parameters
      - trailing  # Optimize trailing stoploss parameters
      - buy  # Optimize buy parameters
      - sell  # Optimize sell parameters
      - protection  # Optimize protection parameters
```

#### Supported Hyperopt Strategies

- **SharpeHyperOptLoss**: Optimizes for risk-adjusted return (Sharpe Ratio).
- **SharpeHyperOptLossDaily**: Optimizes for the Sharpe Ratio on a daily basis.
- **SortinoHyperOptLoss**: Optimizes for downside risk (Sortino Ratio).
- **SortinoHyperOptLossDaily**: Optimizes for downside risk on a daily basis.
- **MaxDrawDownHyperOptLoss**: Minimizes the maximum drawdown (the peak-to-trough decline during a strategy).
- **MaxDrawDownRelativeHyperOptLoss**: Minimizes both absolute and relative drawdown.
- **CalmarHyperOptLoss**: Optimizes the Calmar Ratio (returns relative to drawdown).
- **ProfitDrawDownHyperOptLoss**: Optimizes for both profit and drawdown, balancing risk and reward.
- **OnlyProfitHyperOptLoss**: Focuses solely on maximizing profit.
- **ShortTradeDurHyperOptLoss**: Optimizes for short trade durations, minimizing risk during short periods.

### Data Download

To accurately backtest and optimize strategies, historical data is required. The chart allows you to download market data for specific pairs and timeframes.

```yaml
testing:
  download_data:
    enabled: true  # Enable downloading of historical data
    days: 60  # Number of days to download
    timeframes:
      - "5m"  # Timeframe(s) for which data is downloaded (e.g., 5m, 1d)
    pair_whitelist:
      - "BTC/USDT"  # List of pairs for which data should be downloaded
    dl_trades: false  # Set to true if you want to download trade data from some exchanges (very slow)
```

The downloaded data is then used for backtesting and hyperopt to ensure accurate results.

---

## Persistent Volume Claims (PVC)

To ensure that bot data and strategies persist across restarts and redeployments, this Helm chart supports PVCs (Persistent Volume Claims). This allows the bot to store data such as its state, logs, and strategies in persistent storage.

- **`pvc.data.enabled`**: Enables persistent storage for

 the bot’s data, such as logs and states.
- **`pvc.strategy.enabled`**: Enables persistent storage for trading strategies, ensuring that they are retained across restarts.
- **`pvc.data.size`**: Specifies the size of the storage for bot data (e.g., `1Gi`).
- **`pvc.strategy.size`**: Specifies the size of the storage for strategies (e.g., `1Gi`).

Example configuration:

```yaml
pvc:
  data:
    enabled: true
    size: 1Gi
  strategy:
    enabled: true
    size: 1Gi
```

---

## Strategy

You can define your custom strategy in Python using the `strategy` template provided in the `values.yaml`. The class name is dynamically inserted using the Helm template system.

Here is a sample strategy definition:

```yaml
strategy: |-
  # --- Do not remove these libs ---
  from freqtrade.strategy import IStrategy
  from typing import Dict, List
  from functools import reduce
  from pandas import DataFrame
  # --------------------------------

  import talib.abstract as ta
  import freqtrade.vendor.qtpylib.indicators as qtpylib
  ... other imports

  class {{ .Values.strategyName }}(IStrategy):

      INTERFACE_VERSION: int = 3
      ....
      ....

```

- **`strategyName`**: The name of your strategy is dynamically inserted into the class name.
- **`strategy`**: The actual Python code for your custom strategy, which follows Freqtrade's `IStrategy` interface.

---

## Conclusion

The **freqtrade-testing-helm** chart simplifies the deployment of the Freqtrade trading bot in a Kubernetes environment, enabling backtesting, hyperoptimization, and data downloading for accurate strategy testing. Customize your bot with flexible configuration options, and leverage persistent storage to maintain strategies and bot data across deployments.

---

## License

This Helm chart is open-source and licensed under the MIT License.

