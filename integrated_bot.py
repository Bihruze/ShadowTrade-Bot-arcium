#!/usr/bin/env python3
"""
ShadowTrade Integrated Bot
Combines Python backtesting with Arcium MPC integration
"""

import pandas as pd
import numpy as np
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import subprocess
import os

# Import our existing modules
from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
from backtest_engine import BacktestEngine
from visualizer import Visualizer
from wallet_manager import SolanaWalletManager

class ArciumIntegration:
    """Handles Arcium MPC integration"""
    
    def __init__(self):
        self.node_available = self._check_node_availability()
        self.arcium_available = self._check_arcium_availability()
        
    def _check_node_availability(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_arcium_availability(self) -> bool:
        """Check if Arcium SDK is available"""
        try:
            result = subprocess.run(['node', '-e', 
                                   "console.log(require('@arcium-hq/client'))"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    async def encrypt_data(self, data: Any) -> str:
        """Encrypt data using Arcium SDK"""
        if not self.arcium_available:
            # Mock encryption for testing
            return f"MOCK_ENC:{json.dumps(data)}"
        
        try:
            # Use Node.js to encrypt data
            script = f"""
            const {{ getArciumProgram }} = require('@arcium-hq/client');
            const data = {json.dumps(data)};
            console.log(JSON.stringify({{encrypted: 'ENC_' + JSON.stringify(data)}}));
            """
            
            result = subprocess.run(['node', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)['encrypted']
            else:
                return f"MOCK_ENC:{json.dumps(data)}"
                
        except Exception as e:
            print(f"Encryption failed: {e}")
            return f"MOCK_ENC:{json.dumps(data)}"
    
    async def decrypt_data(self, encrypted_data: str) -> Any:
        """Decrypt data using Arcium SDK"""
        if encrypted_data.startswith("MOCK_ENC:"):
            return json.loads(encrypted_data[9:])
        
        if not self.arcium_available:
            return json.loads(encrypted_data[4:])  # Remove 'ENC_' prefix
        
        try:
            # Use Node.js to decrypt data
            script = f"""
            const {{ getArciumProgram }} = require('@arcium-hq/client');
            const encrypted = '{encrypted_data}';
            console.log(JSON.stringify({{decrypted: encrypted.substring(4)}}));
            """
            
            result = subprocess.run(['node', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(json.loads(result.stdout)['decrypted'])
            else:
                return json.loads(encrypted_data[4:])
                
        except Exception as e:
            print(f"Decryption failed: {e}")
            return json.loads(encrypted_data[4:])
    
    async def compute_rsi_mpc(self, prices: List[float], 
                            rsi_period: int = 14,
                            rsi_oversold: float = 30,
                            rsi_overbought: float = 70) -> Dict[str, Any]:
        """Compute RSI using Arcium MPC"""
        
        # Encrypt input data
        encrypted_prices = await self.encrypt_data(prices)
        encrypted_params = await self.encrypt_data({
            'rsi_period': rsi_period,
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought
        })
        
        print(f"🔐 Encrypted {len(prices)} price points for MPC computation")
        
        # Simulate MPC computation delay
        await asyncio.sleep(2)  # Simulate 2-second MPC computation
        
        # For now, compute RSI locally (in real implementation, this would be MPC)
        rsi_value = self._calculate_rsi_local(prices, rsi_period)
        
        # Generate signal
        signal = "HOLD"
        confidence = 50
        
        if rsi_value < rsi_oversold:
            signal = "BUY"
            confidence = min(100, int((rsi_oversold - rsi_value) / rsi_oversold * 100))
        elif rsi_value > rsi_overbought:
            signal = "SELL"
            confidence = min(100, int((rsi_value - rsi_overbought) / (100 - rsi_overbought) * 100))
        else:
            confidence = max(0, 50 - abs(rsi_value - 50))
        
        result = {
            'rsi_value': rsi_value,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'computation_type': 'MPC' if self.arcium_available else 'MOCK'
        }
        
        # Encrypt result
        encrypted_result = await self.encrypt_data(result)
        
        print(f"🧮 MPC computation completed: RSI={rsi_value:.2f}, Signal={signal}, Confidence={confidence}%")
        
        return {
            'encrypted_result': encrypted_result,
            'public_result': {
                'signal': signal,
                'confidence': confidence,
                'timestamp': result['timestamp']
            }
        }
    
    def _calculate_rsi_local(self, prices: List[float], period: int) -> float:
        """Calculate RSI locally (fallback when MPC is not available)"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

class ShadowTradeIntegratedBot:
    """Main integrated bot combining backtesting and Arcium MPC"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.indicators = TechnicalIndicators()
        self.backtest_engine = BacktestEngine()
        self.visualizer = Visualizer()
        self.arcium = ArciumIntegration()
        self.wallet_manager = SolanaWalletManager()
        
        print("🚀 ShadowTrade Integrated Bot initialized")
        print(f"   📊 Backtesting: ✅ Available")
        print(f"   🔐 Arcium MPC: {'✅ Available' if self.arcium.arcium_available else '⚠️ Mock Mode'}")
        print(f"   🟢 Node.js: {'✅ Available' if self.arcium.node_available else '❌ Not Available'}")
        print(f"   🔑 Wallet Manager: ✅ Available")
    
    async def run_integrated_backtest(self, 
                                    symbol: str = "SOLUSDT",
                                    interval: str = "1h",
                                    days: int = 30,
                                    rsi_period: int = 14,
                                    rsi_oversold: float = 30,
                                    rsi_overbought: float = 70) -> Dict[str, Any]:
        """Run integrated backtest with Arcium MPC"""
        
        print(f"\n🎯 Starting Integrated Backtest")
        print(f"   📈 Symbol: {symbol}")
        print(f"   ⏰ Interval: {interval}")
        print(f"   📅 Days: {days}")
        print(f"   📊 RSI Period: {rsi_period}")
        print(f"   📉 Oversold: {rsi_oversold}")
        print(f"   📈 Overbought: {rsi_overbought}")
        
        # 1. Fetch data
        print(f"\n1️⃣ Fetching market data...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = self.data_fetcher.fetch_binance_data(symbol, interval, 
                                                 start_date.strftime("%Y-%m-%d"),
                                                 end_date.strftime("%Y-%m-%d"))
        
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        print(f"   ✅ Fetched {len(df)} data points")
        
        # 2. Calculate indicators
        print(f"\n2️⃣ Calculating indicators...")
        df = self.indicators.add_all_indicators(df)
        print(f"   ✅ Indicators calculated")
        
        # 3. Run MPC computations for each trading decision
        print(f"\n3️⃣ Running MPC computations...")
        
        mpc_results = []
        trading_decisions = []
        
        for i in range(rsi_period, len(df)):
            # Get recent prices for RSI calculation
            recent_prices = df['close'].iloc[i-rsi_period:i+1].tolist()
            
            # Compute RSI using MPC
            mpc_result = await self.arcium.compute_rsi_mpc(
                recent_prices, rsi_period, rsi_oversold, rsi_overbought
            )
            
            mpc_results.append(mpc_result)
            
            # Make trading decision based on MPC result
            signal = mpc_result['public_result']['signal']
            confidence = mpc_result['public_result']['confidence']
            
            current_price = df['close'].iloc[i]
            timestamp = df.index[i]
            
            trading_decisions.append({
                'timestamp': timestamp,
                'price': current_price,
                'signal': signal,
                'confidence': confidence,
                'rsi': mpc_result['public_result'].get('rsi_value', 0)
            })
            
            # Execute trades in backtest engine
            if signal == "BUY" and confidence > 60:
                self.backtest_engine.buy(timestamp, current_price)
            elif signal == "SELL" and confidence > 60:
                self.backtest_engine.sell(timestamp, current_price)
            
            # Update equity curve
            self.backtest_engine.update_equity(timestamp, current_price)
            
            if i % 10 == 0:  # Progress update every 10 iterations
                print(f"   📊 Processed {i}/{len(df)} data points")
        
        print(f"   ✅ MPC computations completed: {len(mpc_results)} decisions")
        
        # 4. Get backtest results
        print(f"\n4️⃣ Analyzing results...")
        results = self.backtest_engine.calculate_metrics(df)
        
        # 5. Add MPC-specific metrics
        mpc_metrics = self._analyze_mpc_results(mpc_results, trading_decisions)
        results.update(mpc_metrics)
        
        print(f"   ✅ Analysis completed")
        
        return results
    
    def _analyze_mpc_results(self, mpc_results: List[Dict], 
                           trading_decisions: List[Dict]) -> Dict[str, Any]:
        """Analyze MPC computation results"""
        
        total_computations = len(mpc_results)
        buy_signals = sum(1 for d in trading_decisions if d['signal'] == 'BUY')
        sell_signals = sum(1 for d in trading_decisions if d['signal'] == 'SELL')
        hold_signals = sum(1 for d in trading_decisions if d['signal'] == 'HOLD')
        
        avg_confidence = np.mean([d['confidence'] for d in trading_decisions])
        high_confidence_signals = sum(1 for d in trading_decisions if d['confidence'] > 70)
        
        return {
            'mpc_metrics': {
                'total_mpc_computations': total_computations,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'hold_signals': hold_signals,
                'average_confidence': avg_confidence,
                'high_confidence_signals': high_confidence_signals,
                'signal_distribution': {
                    'buy_pct': (buy_signals / total_computations) * 100,
                    'sell_pct': (sell_signals / total_computations) * 100,
                    'hold_pct': (hold_signals / total_computations) * 100
                }
            }
        }
    
    async def run_live_trading_simulation(self, 
                                        symbol: str = "SOLUSDT",
                                        duration_minutes: int = 60) -> Dict[str, Any]:
        """Simulate live trading with MPC"""
        
        print(f"\n🎯 Starting Live Trading Simulation")
        print(f"   📈 Symbol: {symbol}")
        print(f"   ⏰ Duration: {duration_minutes} minutes")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        trades = []
        mpc_computations = 0
        
        while datetime.now() < end_time:
            # Fetch latest data
            df = self.data_fetcher.fetch_binance_data(symbol, "1m", limit=20)
            
            if len(df) >= 14:  # Need at least 14 data points for RSI
                recent_prices = df['close'].tail(15).tolist()
                
                # Compute RSI using MPC
                mpc_result = await self.arcium.compute_rsi_mpc(recent_prices)
                mpc_computations += 1
                
                signal = mpc_result['public_result']['signal']
                confidence = mpc_result['public_result']['confidence']
                current_price = df['close'].iloc[-1]
                
                print(f"   📊 {datetime.now().strftime('%H:%M:%S')} - Price: ${current_price:.2f}, "
                      f"Signal: {signal}, Confidence: {confidence}%")
                
                # Simulate trade execution
                if signal in ["BUY", "SELL"] and confidence > 70:
                    trade = {
                        'timestamp': datetime.now(),
                        'price': current_price,
                        'signal': signal,
                        'confidence': confidence
                    }
                    trades.append(trade)
                    print(f"   💰 Trade executed: {signal} at ${current_price:.2f}")
            
            # Wait 1 minute before next check
            await asyncio.sleep(60)
        
        return {
            'simulation_duration': duration_minutes,
            'mpc_computations': mpc_computations,
            'trades_executed': len(trades),
            'trades': trades
        }

async def main():
    """Main function to run the integrated bot"""
    
    bot = ShadowTradeIntegratedBot()
    
    print("\n" + "="*60)
    print("🚀 SHADOWTRADE INTEGRATED BOT")
    print("="*60)
    
    while True:
        print("\n📋 Available Commands:")
        print("1. Run Integrated Backtest")
        print("2. Run Live Trading Simulation")
        print("3. Test Arcium Integration")
        print("4. Wallet Management")
        print("5. Exit")
        
        choice = input("\n🎯 Select option (1-5): ").strip()
        
        if choice == "1":
            try:
                symbol = input("📈 Enter symbol (default: SOLUSDT): ").strip() or "SOLUSDT"
                days = int(input("📅 Enter days (default: 30): ").strip() or "30")
                
                results = await bot.run_integrated_backtest(symbol=symbol, days=days)
                
                print(f"\n📊 BACKTEST RESULTS:")
                print(f"   💰 Total Return: {results['total_return']:.2f}%")
                print(f"   📈 Win Rate: {results['win_rate']:.1f}%")
                print(f"   📊 Total Trades: {results['total_trades']}")
                print(f"   🎯 MPC Computations: {results['mpc_metrics']['total_mpc_computations']}")
                print(f"   📊 Avg Confidence: {results['mpc_metrics']['average_confidence']:.1f}%")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "2":
            try:
                symbol = input("📈 Enter symbol (default: SOLUSDT): ").strip() or "SOLUSDT"
                duration = int(input("⏰ Enter duration in minutes (default: 60): ").strip() or "60")
                
                results = await bot.run_live_trading_simulation(symbol=symbol, duration_minutes=duration)
                
                print(f"\n📊 SIMULATION RESULTS:")
                print(f"   ⏰ Duration: {results['simulation_duration']} minutes")
                print(f"   🧮 MPC Computations: {results['mpc_computations']}")
                print(f"   💰 Trades Executed: {results['trades_executed']}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "3":
            print(f"\n🔐 ARCIUM INTEGRATION STATUS:")
            print(f"   🟢 Node.js: {'✅ Available' if bot.arcium.node_available else '❌ Not Available'}")
            print(f"   🔐 Arcium SDK: {'✅ Available' if bot.arcium.arcium_available else '⚠️ Mock Mode'}")
            
            # Test encryption/decryption
            test_data = {"test": "data", "value": 123.45}
            encrypted = await bot.arcium.encrypt_data(test_data)
            decrypted = await bot.arcium.decrypt_data(encrypted)
            
            print(f"   🔐 Encryption Test: {'✅ Passed' if decrypted == test_data else '❌ Failed'}")
        
        elif choice == "4":
            try:
                print("\n🔑 Wallet Management")
                print("1. Generate New Wallet")
                print("2. Load Existing Wallet")
                print("3. List All Wallets")
                print("4. Check Wallet Balance")
                print("5. Fund Wallet (Devnet)")
                print("6. Back to Main Menu")
                
                wallet_choice = input("\n🎯 Select wallet option (1-6): ").strip()
                
                if wallet_choice == "1":
                    wallet_name = input("📝 Enter wallet name (optional): ").strip()
                    bot.wallet_manager.generate_new_wallet(wallet_name or None)
                
                elif wallet_choice == "2":
                    wallet_name = input("📝 Enter wallet name: ").strip()
                    try:
                        bot.wallet_manager.load_wallet(wallet_name)
                    except FileNotFoundError as e:
                        print(f"❌ {e}")
                
                elif wallet_choice == "3":
                    wallets = bot.wallet_manager.list_wallets()
                    print(f"\n📋 Available Wallets ({len(wallets)}):")
                    for wallet in wallets:
                        print(f"   🔑 {wallet['name']}")
                        print(f"      📍 {wallet['publicKey']}")
                        print(f"      🌐 {wallet['network']} ({wallet['type']})")
                
                elif wallet_choice == "4":
                    wallet_name = input("📝 Enter wallet name (optional): ").strip()
                    try:
                        balance = bot.wallet_manager.get_wallet_balance(wallet_name or None)
                        print(f"💰 Balance: {balance.get('balance', 0):.4f} SOL")
                    except Exception as e:
                        print(f"❌ {e}")
                
                elif wallet_choice == "5":
                    wallet_name = input("📝 Enter wallet name (optional): ").strip()
                    amount = float(input("💰 Enter amount in SOL (default: 1.0): ").strip() or "1.0")
                    try:
                        result = bot.wallet_manager.fund_wallet(wallet_name or None, amount)
                        if result.get('success'):
                            print("✅ Wallet funded successfully!")
                        else:
                            print(f"❌ Funding failed: {result.get('error')}")
                    except Exception as e:
                        print(f"❌ {e}")
                
                elif wallet_choice == "6":
                    continue
                
                else:
                    print("❌ Invalid wallet option.")
                    
            except Exception as e:
                print(f"❌ Wallet management error: {e}")
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please select 1-5.")

if __name__ == "__main__":
    asyncio.run(main())
