# 🚀 ShadowTrade Integrated Bot

**Private Portfolio Tracker & Trading Bot with Arcium MPC Integration**

ShadowTrade Bot, yatırım stratejilerinizi gizli tutarken otomatik trading yapmanızı sağlayan, Arcium'un Multi-Party Computation (MPC) teknolojisini kullanan gelişmiş bir trading botudur.

## ✨ Özellikler

### 🔐 **Privacy-First Trading**
- **Gizli Stratejiler**: RSI, MACD, Moving Average stratejileri MPC ile gizli hesaplanır
- **Gizli Pozisyonlar**: Portföy detayları şifrelenmiş olarak saklanır
- **Public Performance**: Sadece performans metrikleri herkese açık

### 🧮 **Arcium MPC Integration**
- **Real MPC Computations**: RSI hesaplamaları Arcium ağında yapılır
- **Encrypted Data**: Tüm hassas veriler şifrelenir
- **Privacy-Preserving**: Strateji detayları hiçbir zaman açığa çıkmaz

### 📊 **Advanced Backtesting**
- **Multiple Strategies**: RSI, MACD, MA Cross, Buy & Hold
- **Real Market Data**: Binance API'den gerçek veriler
- **Performance Metrics**: Return, Win Rate, Sharpe Ratio, Max Drawdown
- **Visualization**: Equity curves, trade analysis, drawdown charts

### 🎯 **Copy Trading Ready**
- **Public Leaderboard**: Performans sıralaması
- **Strategy Sharing**: Stratejileri paylaşabilirsiniz
- **Fee System**: Copy trading için ücret sistemi

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   ShadowTrade Bot                       │
│  • Python Backtesting Engine                           │
│  • Real-time Price Feeds                               │
│  • Strategy Execution                                  │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Arcium MPC Network                         │
│  • RSI Computation (Encrypted)                         │
│  • Position Sizing (Encrypted)                         │
│  • Performance Metrics (Encrypted)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Solana Blockchain                          │
│  • Public Performance Metrics                          │
│  • Strategy Registration                               │
│  • Copy Trading Coordination                           │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. **Installation**

```bash
# Clone the repository
git clone <repository-url>
cd shadow-trade-integrated

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Activate virtual environment (if using)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. **Run Integrated Bot**

```bash
# Start the integrated bot
python integrated_bot.py

# Or use npm script
npm start
```

### 3. **Available Commands**

```
📋 Available Commands:
1. Run Integrated Backtest
2. Run Live Trading Simulation  
3. Test Arcium Integration
4. Exit
```

## 📊 Usage Examples

### **Integrated Backtest**
```python
from integrated_bot import ShadowTradeIntegratedBot
import asyncio

async def main():
    bot = ShadowTradeIntegratedBot()
    
    # Run backtest with MPC
    results = await bot.run_integrated_backtest(
        symbol="SOLUSDT",
        days=30,
        rsi_period=14,
        rsi_oversold=30,
        rsi_overbought=70
    )
    
    print(f"Total Return: {results['total_return']:.2f}%")
    print(f"Win Rate: {results['win_rate']:.1f}%")
    print(f"MPC Computations: {results['mpc_metrics']['total_mpc_computations']}")

asyncio.run(main())
```

### **Live Trading Simulation**
```python
# Simulate live trading with MPC
results = await bot.run_live_trading_simulation(
    symbol="SOLUSDT",
    duration_minutes=60
)

print(f"Trades Executed: {results['trades_executed']}")
print(f"MPC Computations: {results['mpc_computations']}")
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Create .env file
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
ARCIUM_NETWORK=testnet  # or mainnet
SOLANA_RPC_URL=https://api.devnet.solana.com
```

### **Strategy Parameters**
```python
# RSI Strategy
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Position Sizing
RISK_PERCENTAGE = 10  # 10% of portfolio
MAX_POSITION_SIZE = 20  # 20% max position

# MPC Settings
MPC_TIMEOUT = 10  # seconds
MPC_RETRY_COUNT = 3
```

## 📈 Performance Metrics

### **Backtest Results**
- **Total Return**: Portfolio return percentage
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted return
- **Max Drawdown**: Maximum loss from peak
- **Profit Factor**: Gross profit / Gross loss

### **MPC Metrics**
- **Total Computations**: Number of MPC calls
- **Average Confidence**: Signal confidence level
- **High Confidence Signals**: Signals with >70% confidence
- **Computation Time**: Average MPC execution time

## 🧪 Testing

### **Run All Tests**
```bash
# Python tests
python -m pytest tests/

# Arcium SDK tests
npm run test-arcium

# MXE program tests
npm run test-mxe

# Circuit tests
npm run test-circuit
```

### **Individual Tests**
```bash
# Test Arcium integration
node test-arcium-fixed.js

# Test MXE program
node test-mxe.js

# Test RSI circuit
node test-circuit.js
```

## 🔐 Security Features

### **Data Encryption**
- **Price Data**: Encrypted before MPC computation
- **Strategy Parameters**: Never exposed in plain text
- **Position Sizes**: Calculated in encrypted MPC
- **Performance Data**: Only public metrics are visible

### **Privacy Guarantees**
- **Strategy Logic**: Completely hidden
- **Trade Amounts**: Encrypted calculations
- **Portfolio Details**: Private to user only
- **MPC Verification**: All computations are verifiable

## 📚 Documentation

### **Core Components**
- [`integrated_bot.py`](integrated_bot.py) - Main bot implementation
- [`backtest_engine.py`](backtest_engine.py) - Backtesting engine
- [`data_fetcher.py`](data_fetcher.py) - Market data fetching
- [`indicators.py`](indicators.py) - Technical indicators
- [`visualizer.py`](visualizer.py) - Results visualization

### **Arcium Integration**
- [`mxe-program.rs`](mxe-program.rs) - Solana MXE program
- [`rsi-circuit.circom`](rsi-circuit.circom) - RSI MPC circuit
- [`test-arcium-fixed.js`](test-arcium-fixed.js) - Arcium SDK tests
- [`test-mxe.js`](test-mxe.js) - MXE program tests
- [`test-circuit.js`](test-circuit.js) - Circuit tests

### **Documentation Files**
- [`REAL_ARCIUM_INTEGRATION.md`](REAL_ARCIUM_INTEGRATION.md) - Complete integration guide
- [`README.md`](README.md) - This file

## 🚀 Deployment

### **Development**
```bash
# Local development
python integrated_bot.py

# With hot reload
python -m uvicorn integrated_bot:app --reload
```

### **Production**
```bash
# Build for production
docker build -t shadow-trade-bot .

# Run in production
docker run -p 8000:8000 shadow-trade-bot
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/shadow-trade/wiki)
- **Issues**: [GitHub Issues](https://github.com/shadow-trade/issues)
- **Discord**: [ShadowTrade Community](https://discord.gg/shadow-trade)
- **Email**: support@shadow-trade.com

## 🎯 Roadmap

### **Phase 1: Core Integration** ✅
- [x] Python backtesting engine
- [x] Arcium MPC integration
- [x] RSI strategy implementation
- [x] Basic visualization

### **Phase 2: Advanced Features** 🚧
- [ ] Multiple strategy support
- [ ] Real-time trading
- [ ] Copy trading system
- [ ] Mobile app

### **Phase 3: Production** 📋
- [ ] Mainnet deployment
- [ ] Advanced analytics
- [ ] API marketplace
- [ ] Enterprise features

---

**ShadowTrade Bot** - *Privacy-First Trading with MPC Technology* 🚀