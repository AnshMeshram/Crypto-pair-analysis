# Real-time Crypto Pair Analytics Dashboard

## 📊 What is this Project?

This is a **live trading analytics application** designed for quantitative traders and researchers. It streams real-time cryptocurrency price data from Binance, stores it locally, calculates statistical trading signals (like spreads and z-scores), and displays everything through an easy-to-use web dashboard.

**Think of it as:** A mini Bloomberg terminal for crypto pairs that helps you spot trading opportunities in real-time.

## 🎯 What Does It Do?

1. **Real-time Data Streaming**: Connects to Binance's live market data feed and receives price updates every millisecond
2. **Data Storage**: Saves all price ticks to a local database so you can analyze historical patterns
3. **Pair Trading Analytics**: Compares two cryptocurrencies to find trading opportunities when their prices diverge
4. **Visual Dashboard**: Shows interactive charts with prices, spreads, and statistical indicators
5. **Smart Alerts**: Notifies you when trading signals meet your criteria
6. **Data Export**: Download your analysis results as CSV files

## 🏗️ How Does It Work?

```text
┌─────────────────┐
│  Binance API    │ ← Live market data (BTC, ETH, etc.)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ WebSocket       │ ← backend.py connects and listens
│ Ingestion       │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ SQLite Database │ ← data_store.py saves every tick
│  (ticks.db)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Analytics       │ ← analytics.py calculates signals
│ Engine          │    (hedge ratio, z-score, ADF test)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Streamlit       │ ← app.py displays interactive charts
│ Dashboard       │
└─────────────────┘
         ↓
   Your Browser (localhost:8501)
```

**Step-by-step flow:**

1. **Ingestion**: The app connects to Binance and receives real-time trades (price + quantity)
2. **Storage**: Each trade is stored in `ticks.db` with timestamp, symbol, price, and quantity
3. **Resampling**: Tick data is aggregated into candlesticks (1 second, 1 minute, or 5 minutes)
4. **Analytics**: For any two symbols (e.g., BTC vs ETH), the app calculates:
   - **Hedge Ratio**: How much of asset X you need to hedge asset Y
   - **Spread**: The price difference between the pair
   - **Z-Score**: How many standard deviations the spread is from its mean (indicates overbought/oversold)
   - **ADF Test**: Statistical test to check if the spread is mean-reverting
5. **Visualization**: All results are plotted in real-time on interactive charts
6. **Alerts**: When z-score crosses your threshold, you get notified

## 🚀 Quick Start Guide (For Absolute Beginners)

### Prerequisites

- **Python 3.8+** installed on your computer ([Download here](https://www.python.org/downloads/))
- **Internet connection** (to stream live data from Binance)
- **Command Prompt or Terminal** access

### Step 1: Download the Project

Save all project files to a folder, for example: `C:\Users\YourName\Desktop\qea`

### Step 2: Open Command Prompt

- Press `Windows Key + R`
- Type `cmd` and press Enter
- Navigate to your project folder:

```cmd
cd C:\Users\YourName\Desktop\qea
```

### Step 3: Create a Virtual Environment (Recommended)

This keeps your project dependencies isolated:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

You'll see `(.venv)` appear in your command prompt.

### Step 4: Install Dependencies

```cmd
pip install -r requirements.txt
```

This installs all the libraries the project needs (takes 1-2 minutes).

### Step 5: Run the Application

```cmd
python -m streamlit run app.py
```

### Step 6: Open Your Browser

- The app will automatically open at `http://localhost:8501`
- If it doesn't, manually open your browser and go to that address

### Step 7: Start Ingesting Data

- In the dashboard sidebar, click **"Start Ingest"**
- Wait 10-20 seconds for data to accumulate
- Charts will start updating automatically!

## 📦 Dependencies & Frameworks Explained

### Core Framework

- **Streamlit** (`streamlit>=1.18`)
  - _What it does_: Creates the web dashboard without needing HTML/CSS/JavaScript
  - _Why we use it_: Fast prototyping, built-in widgets, auto-refresh capabilities

### Data Handling

- **Pandas** (`pandas>=1.5`)
  - _What it does_: Manipulates and analyzes tabular data (like Excel on steroids)
  - _Why we use it_: Resampling ticks to candlesticks, time series operations
- **NumPy** (`numpy>=1.23`)

  - _What it does_: Fast numerical computations and linear algebra
  - _Why we use it_: Calculating hedge ratios via linear regression

- **SQLAlchemy** (`sqlalchemy>=1.4`)
  - _What it does_: Database toolkit (though we use raw SQLite3 for simplicity)
  - _Why we use it_: Provides advanced DB features if needed later

### Real-time Communication

- **WebSockets** (`websockets>=11.0`)
  - _What it does_: Maintains persistent connection to Binance for live data
  - _Why we use it_: Much faster than polling; receives updates instantly

### Visualization

- **Plotly** (`plotly>=5.6`)
  - _What it does_: Creates interactive charts (zoom, pan, hover tooltips)
  - _Why we use it_: Professional-looking charts with zero effort

### Statistical Analysis

- **Statsmodels** (`statsmodels>=0.13`)
  - _What it does_: Advanced statistical tests and models
  - _Why we use it_: ADF test for stationarity, time series analysis

## 📁 Project Structure

```text
qea/
│
├── app.py                  # Main Streamlit dashboard (START HERE)
├── backend.py              # WebSocket ingestion from Binance
├── data_store.py           # SQLite database manager
├── analytics.py            # Statistical calculations
├── requirements.txt        # List of Python packages needed
├── README.md              # This file!
├── diagram.drawio         # Architecture diagram (editable)
├── diagram.svg            # Architecture diagram (image)
│
├── ticks.db               # SQLite database (created automatically)
├── check_db.py            # Utility to inspect database contents
└── run_ingest.py          # Standalone ingestion test script
```

## 🎨 Key Features Explained

### 1. Symbol Selection

Choose which cryptocurrencies to track (default: BTCUSDT, ETHUSDT, BNBUSDT)

### 2. Timeframe Resampling

- **1S**: 1-second candlesticks (high-frequency view)
- **1T**: 1-minute candlesticks (medium-frequency)
- **5T**: 5-minute candlesticks (lower-frequency)

### 3. Pair Analytics

Select exactly 2 symbols to analyze their relationship:

- **Hedge Ratio (β)**: From regression Y = α + βX
- **Spread**: Y - (α + βX) — measures divergence
- **Z-Score**: (Spread - Mean) / StdDev — normalized signal
- **ADF Test**: Tests if spread is mean-reverting (p-value < 0.05 = stationary)

### 4. CSV Upload

Upload your own historical OHLC data to test analytics offline

### 5. Alerts

Set a z-score threshold (e.g., 2.0) to get notified when extreme divergences occur

### 6. Data Export

Download all calculated data (prices, spreads, z-scores) as CSV

## 🔧 Design Decisions & Trade-offs

### Why SQLite?

- ✅ Zero configuration, single file database
- ✅ Perfect for local prototypes
- ❌ For production: Use TimescaleDB (time-series optimized) or InfluxDB

### Why Single-Process Architecture?

- ✅ Simple to run (one command)
- ✅ Easy to debug
- ❌ For scale: Separate ingestion (Kafka/Redis) from analytics (microservices)

### Why OLS Regression?

- ✅ Fast, simple, interpretable
- ✅ Good baseline for hedge ratio
- ❌ For production: Add Kalman Filter (adapts to changing relationships) or Robust Regression (handles outliers)

## 🧪 Testing Your Setup

### Test 1: Verify Ingestion

```cmd
python run_ingest.py
```

Should print "Starting ingest for 20s..." and collect data.

### Test 2: Check Database

```cmd
python check_db.py
```

Should show tick counts for each symbol (e.g., BTCUSDT: 1123).

### Test 3: Run Full App

```cmd
python -m streamlit run app.py
```

Open browser to `http://localhost:8501` and click "Start Ingest".

## 🎓 Key Concepts for Beginners

### What is a "Tick"?

A single trade event: timestamp, symbol, price, quantity

### What is OHLC?

**O**pen, **H**igh, **L**ow, **C**lose prices for a time period (like a candlestick)

### What is a Spread?

The price difference between two assets after adjusting for their correlation

### What is a Z-Score?

Measures how far the current value is from average (in standard deviations)

- Z > 2: Abnormally high (potential sell signal)
- Z < -2: Abnormally low (potential buy signal)
- Z ≈ 0: Near average (no signal)

### What is Mean Reversion?

A trading strategy that bets prices will return to their average after extreme moves

## 📊 Files You'll Interact With

### As a User

- **app.py**: Run this to start the dashboard
- **requirements.txt**: Install dependencies from here

### As a Developer

- **backend.py**: Modify to add new data sources (e.g., other exchanges)
- **analytics.py**: Add new calculations (e.g., Kalman filter, Bollinger bands)
- **data_store.py**: Change database schema or switch to PostgreSQL

## 🚨 Troubleshooting

### "Module not found" errors

```cmd
pip install -r requirements.txt
```

Make sure you're in the project folder and virtual environment is activated.

### Streamlit won't start

Try:

```cmd
python -m streamlit run app.py
```

Instead of just `streamlit run app.py`.

### No data appearing

1. Click "Start Ingest" button in the sidebar
2. Wait 10-20 seconds for data to accumulate
3. Ensure you have internet connection to reach Binance

### Database locked errors

Close any other Python processes accessing `ticks.db`:

```cmd
taskkill /F /IM python.exe
```

## 🎯 Next Steps / Extensions

Once you're comfortable with the basics, consider adding:

- **Kalman Filter**: Dynamic hedge estimation that adapts over time
- **Robust Regression**: Huber or Theil-Sen for outlier-resistant hedge ratios
- **Backtesting Module**: Test mean-reversion strategies (z>2 entry, z<0 exit)
- **Multi-Exchange Support**: Add Coinbase, Kraken data sources
- **Message Broker**: Use Redis or Kafka to decouple ingestion from analytics
- **Advanced Alerts**: Email/Telegram notifications, multiple alert rules
- **Risk Metrics**: VaR, Sharpe ratio, drawdown analysis

## 📚 Learning Resources

### Understanding Pair Trading

- [Investopedia: Pairs Trading](https://www.investopedia.com/terms/p/pairstrade.asp)
- [QuantStart: Statistical Arbitrage](https://www.quantstart.com/articles/)

### Python for Finance

- [Python for Finance by Yves Hilpisch](https://www.oreilly.com/library/view/python-for-finance/9781492024323/)
- [Algorithmic Trading with Python](https://www.datacamp.com/courses/algorithmic-trading-with-python)

### Time Series Analysis

- [Statsmodels Documentation](https://www.statsmodels.org/)
- [Pandas Time Series Guide](https://pandas.pydata.org/docs/user_guide/timeseries.html)

## 🤝 ChatGPT Usage Transparency

This project scaffold and code were generated with assistance from an AI coding assistant (GitHub Copilot using Claude Sonnet 4.5) to speed implementation and produce clear structure.

**Prompts used:**

- "Create a Streamlit dashboard for real-time crypto pair analytics"
- "Implement Binance WebSocket ingestion with SQLite storage"
- "Add OLS hedge ratio, spread calculation, z-score, and ADF test"
- "Create interactive Plotly charts with controls for timeframe and symbols"
- "Add CSV export and alert functionality"

The AI handled boilerplate code, structure, and integration. Human review ensured correctness, usability, and alignment with quantitative finance best practices.

## 📜 License

This prototype is provided as-is for evaluation purposes. Feel free to modify and extend for educational or commercial use.

## 📧 Support

If you encounter issues:

1. Check the Troubleshooting section above
2. Review the project structure and ensure all files are present
3. Verify Python version (3.8+) and internet connectivity
4. Check `ticks.db` exists and has data using `python check_db.py`

---

Built with ❤️ for quantitative traders and researchers
