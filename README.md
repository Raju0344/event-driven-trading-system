# Event Driven Trading System

A modular **event-driven trading engine** designed for both **live trading** and **historical backtesting**.
The system separates market data, strategy logic, risk management, and portfolio management using an event-driven architecture similar to professional quantitative trading systems.

---

# System Architecture

The trading engine follows an **event-driven architecture** where different components communicate through events such as:

* Market Event
* Signal Event
* Order Event
* Fill Event

This design allows strategies to run seamlessly in both **live trading environments** and **backtesting simulations**.

Project Structure:

```
event-driven-trading-system/

│
├── broker/           # Broker integrations (e.g., Zerodha, Alpaca, Binance)
├── config/           # JSON/YAML configuration files (API keys, database settings)
├── core/             # Core engine and event loop implementation
├── data/             # Data handlers (live_data_handler, simulated_data_handler)
├── execution/        # Order execution modules (live_execution, simulated_execution)
├── logs/             # Logging configuration and log storage
├── output/           # Performance outputs (Sharpe ratio, metrics reports)
├── plot/             # Plotting utilities (drawdown, returns, equity curve)
├── portfolio/        # Portfolio management and performance tracking
├── risk/             # Position sizing and risk management modules
├── strategy/         # Strategy implementations and strategy registry
├── utils/            # Utility modules (logger, config loader, helpers)
│
├── main.py           # Entry point that combines all system components
├── requirements.txt  # Project dependencies
└── README.md         # Project documentation

```

---

# 1️⃣ Live Trading

The live trading module connects the event-driven system to a **real broker or exchange API**.

## Live Trading Workflow

```
Market Data → Strategy → Signal → Portfolio → Risk Management → Order Execution → Portfolio Update
```

### Components

**Market Data Handler**

Receives real-time market data from an exchange API.

Examples:

* Zerodha

**Strategy Engine**

Processes incoming market events and generates trading signals.

Example signals:

* BUY
* SELL
* HOLD

**Risk Management**

Ensures trades follow predefined risk rules:

* Position sizing
* Maximum exposure
* Stop-loss rules

**Order Execution**

Sends orders to the broker/exchange API.

Example order types:

* Market Order
* Limit Order

**Portfolio Manager**

Tracks:

* Open positions
* Cash balance
* Profit & Loss (PnL)

---

### Example Live Trading Flow

```
New Market Price
      ↓
Strategy Generates Signal
      ↓
Portfolio Receives Signal
      ↓
Risk Manager Validates Trade
      ↓
Order Sent to Exchange
      ↓
Fill Event Received
      ↓
Portfolio Updated
```

## Live Trading Setup (Zerodha)

To run the system in **live trading mode**, follow these steps:

```json
{
    "COMMENT_1": "********************MYSQL DETAILS**************************",
    "USER": "USER NAME OF YOUR DATA BASE",
    "RAW_PASSWORD": "YOUR DATABASE PASSWORD",
    "HOST": "localhost",
    "DB": "YOUR DATABASE NAME",
    "working_directory": "/home/raju/MAIN_DIRECTORY/zerodha",

    "COMMENT_2": "*********************LIVE DETAILS************************************",
    "api_key": "WRITE YOUR API KEY OF ZERODHA",
    "api_secret": "WRITE YOUR API SECRET OF ZERODHA",
    "request_token": "WRITE YOUR REQUEST TOKEN OF ZERODHA",
    "access_token": "WRITE YOUR ACCESS TOKEN OF ZERODHA",
    "exchange": "NSE",

    "COMMENT_3": "******************************HISTORICAL DATA*****************",
    "last_updated_date": "2026-02-10T16:41:23.080945",
    "time_frame": "5minute",

    "COMMENT_4": "*******************BACKTESTING DETAILS******************************",
    "initial_capital": 10000,
    "heartbeat": 0,
    "start_date": "2026-01-22T00:00:00",
    "sequential_processing": false,
    "mode": "live",
    "symbol_list": [
        "YESBANK",
        "PSB"
    ]
}
```

### 1. Change the Mode

In the configuration file, set:

```json
"mode": "live"
```

### 2. Add Zerodha API Credentials

Update the following fields in your configuration file:

```json
"api_key": "YOUR_ZERODHA_API_KEY",
"api_secret": "YOUR_ZERODHA_API_SECRET"
```

---

### 3. Generate Access Token

Run the following command:

```bash
python3 -m broker.generate_access_token
```

During execution, the program will prompt you to enter:

* Your **Zerodha account password**
* Your **6-digit app code (2FA)**

After successful authentication, the system will automatically generate:

* **request_token**
* **access_token**

These tokens will be used for authenticated trading through the Zerodha API.

---
### 3. Run the system

```bash
python3 main.py
```

### Important Requirement

Ensure that the **ChromeDriver** executable is present in the **working directory** before running the command.

Example:

```
project_directory/
│
├── chromedriver
├── broker/
├── strategy/
├── main.py
```

ChromeDriver is required for automated login during token generation.





---

# 2️⃣ Backtesting

The backtesting module allows strategies to be tested on **historical market data**.

This helps evaluate strategy performance before deploying it to live trading.

## Backtesting Workflow

Historical Data → Strategy → Signal → Portfolio → Simulated Order → Portfolio Update → Performance Metrics

### Components

**Historical Data Handler**

Loads historical data such as:

* Database
* Exchange historical API

Example:

```
timestamp, open, high, low, close, volume
```

---

**Strategy Engine**

The same strategy used in live trading can run in backtesting.

Example strategies:

* Moving Average Crossover
* Mean Reversion
* Momentum
* Statistical Arbitrage

---

**Execution Simulator**

Simulates order execution including:

* Slippage
* Transaction costs

---

**Portfolio Tracker**

Calculates:

* Equity curve
* Drawdown
* Returns
* Sharpe ratio

---

### Backtest Flow

```
Historical Price Data
       ↓
Market Event Generated
       ↓
Strategy Generates Signal
       ↓
Portfolio Receives Signal
       ↓
Simulated Order Execution
       ↓
Portfolio Updated
       ↓
Performance Metrics Calculated
```

---

# Configuration Example

The system uses a **JSON configuration file** to store database credentials, API keys, trading settings, and backtesting parameters.

Example configuration:

```json
{
    "COMMENT_1": "********************MYSQL DETAILS**************************",
    "USER": "USER NAME OF YOUR DATA BASE",
    "RAW_PASSWORD": "YOUR DATABASE PASSWORD",
    "HOST": "localhost",
    "DB": "YOUR DATABASE NAME",
    "working_directory": "/home/raju/MAIN_DIRECTORY/zerodha",

    "COMMENT_2": "*********************LIVE DETAILS************************************",
    "api_key": "WRITE YOUR API KEY OF ZERODHA",
    "api_secret": "WRITE YOUR API SECRET OF ZERODHA",
    "request_token": "WRITE YOUR REQUEST TOKEN OF ZERODHA",
    "access_token": "WRITE YOUR ACCESS TOKEN OF ZERODHA",
    "exchange": "NSE",

    "COMMENT_3": "******************************HISTORICAL DATA*****************",
    "last_updated_date": "2026-02-10T16:41:23.080945",
    "time_frame": "5minute",

    "COMMENT_4": "*******************BACKTESTING DETAILS******************************",
    "initial_capital": 10000,
    "heartbeat": 0,
    "start_date": "2026-01-22T00:00:00",
    "sequential_processing": false,
    "mode": "backtesting",
    "symbol_list": [
        "YESBANK",
        "PSB"
    ]
}
```

This configuration controls:

* Database connection
* Zerodha API authentication
* Historical data settings
* Backtesting parameters
* Symbols used in trading

## Backtesting Setup

To run the system in **backtesting mode**, follow the steps below.

### 1. Create the Database

First, create a **MySQL database** and update the database credentials in the configuration file.

In `config.json`, provide the following details:

* Database **user name**
* Database **password**
* **Host**
* **Database name**

Example:

```json
{
  "USER": "YOUR_DATABASE_USERNAME",
  "RAW_PASSWORD": "YOUR_DATABASE_PASSWORD",
  "HOST": "localhost",
  "DB": "YOUR_DATABASE_NAME"
}
```

---

### 2. Update Configuration

Modify the configuration file to enable **backtesting mode**:

```json
"mode": "backtesting"
```

---

### 3. Download Historical Data

Before running the backtest, make sure that the **historical market data** has been downloaded and stored in the database.

The system will read historical OHLCV data from the database during simulation.

---

### 4. Run the Backtest

Execute the following command to start the backtesting engine:

```bash
python3 main.py
```

The engine will process historical market events, generate signals using the selected strategy, simulate order execution, and calculate portfolio performance.

---

### Database Schema

The required **database schema** for storing historical market data is provided below.


---

# Running the System

Install dependencies:

```
pip install -r requirements.txt
```

Run the trading engine:

```
python3 main.py
```

---

# Key Features

* Event-driven architecture
* Strategy modularity
* Live trading capability
* Historical backtesting
* Risk management module
* Portfolio tracking
* WebSocket market data feed

---

# Future Improvements

* Multi-asset support
* Option trading support
* Advanced risk models
* Performance analytics dashboard
* Reinforcement learning strategies

---

## Database Setup (MySQL)

To run the backtesting engine, a **MySQL database** must be created to store exchange, symbol, and historical price data.

You can install either:

* **MySQL Server**
* **MySQL Workbench**

Use whichever environment you are comfortable with.

---

## 1. Create the Database

Run the following SQL command:

```sql
CREATE DATABASE indian_stock_market;
```

---

## 2. Use the Database

```sql
USE indian_stock_market;
```

---

# Database Schema

The following tables are required by the trading system.

---

## 3. Exchange Table

```sql
CREATE TABLE `exchange` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `abbrev` VARCHAR(32) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `city` VARCHAR(255),
    `country` VARCHAR(255),
    `currency` VARCHAR(64),
    `timezone_offset` TIME,
    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_updated_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;
```

---

## 4. Data Vendor Table

```sql
CREATE TABLE `data_vendor` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(64) NOT NULL,
    `website_url` VARCHAR(255) DEFAULT NULL,
    `support_email` VARCHAR(255) DEFAULT NULL,
    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_updated_date` DATETIME NOT NULL 
        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;
```

---

## 5. Symbol Table

```sql
CREATE TABLE `symbol` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `exchange_id` INT UNSIGNED,
    `ticker` VARCHAR(32) NOT NULL,
    `instrument` VARCHAR(64) NOT NULL,
    `name` VARCHAR(255),
    `sector` VARCHAR(255),
    `currency` VARCHAR(255),
    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_updated_date` DATETIME NOT NULL 
        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_symbol_exchange`
        FOREIGN KEY (`exchange_id`)
        REFERENCES `exchange`(`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;
```

---

## 6. Price Table

```sql
CREATE TABLE `daily_price` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `data_vendor_id` INT UNSIGNED,
    `symbol_id` INT UNSIGNED,
    `price_date` DATETIME NOT NULL,
    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_updated_date` DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `open_price` DECIMAL(19,4),
    `high_price` DECIMAL(19,4),
    `low_price` DECIMAL(19,4),
    `close_price` DECIMAL(19,4),
    `volume` BIGINT UNSIGNED,

    INDEX `idx_daily_price_symbol` (`symbol_id`),
    INDEX `idx_daily_price_vendor` (`data_vendor_id`),
    INDEX `idx_daily_price_date` (`price_date`),

    CONSTRAINT `fk_daily_price_symbol`
        FOREIGN KEY (`symbol_id`)
        REFERENCES `symbol`(`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT `fk_daily_price_data_vendor`
        FOREIGN KEY (`data_vendor_id`)
        REFERENCES `data_vendor`(`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4;
```

---

# Loading Historical Data

After creating the database and tables:

1. Download **historical symbol data**
2. Download **historical price data**

The project includes a script to assist with this process.

Refer to:

```
data/historical_data.py
```

This script loads symbol and price data into the database for use in the **backtesting engine**.

