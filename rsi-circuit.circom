// RSI Circuit for Arcium MPC
// This circuit calculates RSI (Relative Strength Index) in a privacy-preserving manner

pragma circom 2.0.0;

// Template for RSI calculation
template RSI(n) {
    // Input signals
    signal input prices[n];           // Array of prices
    signal input rsi_period;          // RSI period (typically 14)
    signal input rsi_oversold;        // Oversold threshold (typically 30)
    signal input rsi_overbought;      // Overbought threshold (typically 70)
    
    // Output signals
    signal output rsi_value;          // Calculated RSI value
    signal output signal_action;      // Trading signal (0=HOLD, 1=BUY, 2=SELL)
    signal output confidence;         // Signal confidence (0-100)
    
    // Internal signals for calculations
    signal gains[n-1];                // Price gains
    signal losses[n-1];               // Price losses
    signal avg_gain;                  // Average gain
    signal avg_loss;                  // Average loss
    signal rs;                        // Relative strength
    signal rsi;                       // RSI value
    
    // Calculate price changes
    for (var i = 0; i < n-1; i++) {
        gains[i] <== (prices[i+1] - prices[i]) * (prices[i+1] > prices[i] ? 1 : 0);
        losses[i] <== (prices[i] - prices[i+1]) * (prices[i] > prices[i+1] ? 1 : 0);
    }
    
    // Calculate average gain and loss over the period
    var sum_gains = 0;
    var sum_losses = 0;
    
    for (var i = 0; i < rsi_period; i++) {
        sum_gains += gains[i];
        sum_losses += losses[i];
    }
    
    avg_gain <== sum_gains / rsi_period;
    avg_loss <== sum_losses / rsi_period;
    
    // Calculate RS (Relative Strength)
    rs <== avg_gain / (avg_loss + 1); // Add 1 to avoid division by zero
    
    // Calculate RSI
    rsi <== 100 - (100 / (1 + rs));
    rsi_value <== rsi;
    
    // Generate trading signal
    signal_action <== (rsi < rsi_oversold ? 1 : (rsi > rsi_overbought ? 2 : 0));
    
    // Calculate confidence based on how far RSI is from neutral (50)
    confidence <== (rsi < rsi_oversold ? (rsi_oversold - rsi) * 2 : 
                   (rsi > rsi_overbought ? (rsi - rsi_overbought) * 2 : 
                   50 - (rsi > 50 ? rsi - 50 : 50 - rsi)));
}

// Template for position sizing
template PositionSize() {
    // Input signals
    signal input balance;             // Account balance
    signal input risk_percentage;     // Risk percentage (0-100)
    signal input current_price;       // Current token price
    
    // Output signals
    signal output position_value;     // Position value
    signal output position_size;      // Position size in tokens
    
    // Calculate position value
    position_value <== balance * risk_percentage / 100;
    
    // Calculate position size
    position_size <== position_value / current_price;
}

// Template for performance metrics
template PerformanceMetrics(n) {
    // Input signals
    signal input trades[n];           // Array of trade results (1=win, 0=loss)
    signal input initial_balance;     // Initial balance
    signal input current_balance;     // Current balance
    
    // Output signals
    signal output total_return;       // Total return percentage
    signal output win_rate;           // Win rate percentage
    signal output total_trades;       // Total number of trades
    signal output win_trades;         // Number of winning trades
    
    // Calculate total trades
    total_trades <== n;
    
    // Calculate winning trades
    var wins = 0;
    for (var i = 0; i < n; i++) {
        wins += trades[i];
    }
    win_trades <== wins;
    
    // Calculate win rate
    win_rate <== wins * 100 / n;
    
    // Calculate total return
    total_return <== (current_balance - initial_balance) * 100 / initial_balance;
}

// Main component that combines all calculations
template ShadowTradeRSI(n) {
    // Input signals
    signal input prices[n];           // Price data
    signal input rsi_period;          // RSI period
    signal input rsi_oversold;        // Oversold threshold
    signal input rsi_overbought;      // Overbought threshold
    signal input balance;             // Account balance
    signal input risk_percentage;     // Risk percentage
    signal input current_price;       // Current price
    
    // Output signals
    signal output rsi_value;          // RSI value
    signal output signal_action;      // Trading signal
    signal output confidence;         // Signal confidence
    signal output position_value;     // Position value
    signal output position_size;      // Position size
    
    // RSI calculation component
    component rsi_calc = RSI(n);
    rsi_calc.prices <== prices;
    rsi_calc.rsi_period <== rsi_period;
    rsi_calc.rsi_oversold <== rsi_oversold;
    rsi_calc.rsi_overbought <== rsi_overbought;
    
    // Position sizing component
    component pos_size = PositionSize();
    pos_size.balance <== balance;
    pos_size.risk_percentage <== risk_percentage;
    pos_size.current_price <== current_price;
    
    // Connect outputs
    rsi_value <== rsi_calc.rsi_value;
    signal_action <== rsi_calc.signal_action;
    confidence <== rsi_calc.confidence;
    position_value <== pos_size.position_value;
    position_size <== pos_size.position_size;
}

// Export the main component
component main = ShadowTradeRSI(20); // Support up to 20 price points
