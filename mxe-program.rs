use anchor_lang::prelude::*;
use arcis::prelude::*;

declare_id!("ShadowTrade111111111111111111111111111111111");

#[program]
pub mod shadow_trade_mxe {
    use super::*;

    /// Initialize the ShadowTrade MXE program
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let mxe = &mut ctx.accounts.mxe;
        mxe.authority = ctx.accounts.authority.key();
        mxe.bump = ctx.bumps.mxe;
        
        msg!("ShadowTrade MXE initialized by: {}", ctx.accounts.authority.key());
        Ok(())
    }

    /// Define RSI computation for private evaluation
    #[arcis::computation]
    pub fn evaluate_rsi_strategy(
        ctx: Context<EvaluateRSI>,
        encrypted_prices: EncryptedData,
        rsi_period: u8,
        rsi_oversold: u8,
        rsi_overbought: u8,
    ) -> Result<EncryptedData> {
        // This computation will be executed in MPC
        // The actual RSI calculation happens in the circuit
        
        msg!("RSI strategy evaluation requested");
        msg!("RSI Period: {}, Oversold: {}, Overbought: {}", 
             rsi_period, rsi_oversold, rsi_overbought);
        
        // The computation result will be encrypted and returned
        // For now, we'll return a mock encrypted result
        // In real implementation, this would be the actual MPC result
        
        Ok(encrypted_prices) // Mock return - in real implementation, this would be the computed RSI signal
    }

    /// Define position sizing computation
    #[arcis::computation]
    pub fn calculate_position_size(
        ctx: Context<CalculatePosition>,
        encrypted_balance: EncryptedData,
        risk_percentage: u8,
        current_price: u64,
    ) -> Result<EncryptedData> {
        // This computation calculates position size in MPC
        // Formula: (balance * risk_percentage / 100) / current_price
        
        msg!("Position size calculation requested");
        msg!("Risk percentage: {}%, Current price: {}", risk_percentage, current_price);
        
        // Mock return - in real implementation, this would be the calculated position size
        Ok(encrypted_balance)
    }

    /// Define performance metrics computation
    #[arcis::computation]
    pub fn calculate_performance_metrics(
        ctx: Context<CalculatePerformance>,
        encrypted_trades: EncryptedData,
        encrypted_initial_balance: EncryptedData,
    ) -> Result<EncryptedData> {
        // This computation calculates performance metrics in MPC
        // Metrics: total return, win rate, sharpe ratio, max drawdown
        
        msg!("Performance metrics calculation requested");
        
        // Mock return - in real implementation, this would be the calculated metrics
        Ok(encrypted_trades)
    }

    /// Public function to update strategy performance (non-encrypted)
    pub fn update_strategy_performance(
        ctx: Context<UpdatePerformance>,
        total_return: i64, // in basis points
        win_rate: u16,     // in basis points
        total_trades: u32,
        win_trades: u32,
    ) -> Result<()> {
        let strategy = &mut ctx.accounts.strategy;
        
        strategy.total_return = total_return;
        strategy.win_rate = win_rate;
        strategy.total_trades = total_trades;
        strategy.win_trades = win_trades;
        strategy.last_updated = Clock::get()?.unix_timestamp;
        
        msg!("Strategy performance updated: {}% return, {}% win rate", 
             total_return as f64 / 100.0, win_rate as f64 / 100.0);
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + MXE::INIT_SPACE,
        seeds = [b"shadow-trade-mxe"],
        bump
    )]
    pub mxe: Account<'info, MXE>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct EvaluateRSI<'info> {
    #[account(
        mut,
        seeds = [b"shadow-trade-mxe"],
        bump = mxe.bump,
    )]
    pub mxe: Account<'info, MXE>,
    
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct CalculatePosition<'info> {
    #[account(
        mut,
        seeds = [b"shadow-trade-mxe"],
        bump = mxe.bump,
    )]
    pub mxe: Account<'info, MXE>,
    
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct CalculatePerformance<'info> {
    #[account(
        mut,
        seeds = [b"shadow-trade-mxe"],
        bump = mxe.bump,
    )]
    pub mxe: Account<'info, MXE>,
    
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct UpdatePerformance<'info> {
    #[account(
        init_if_needed,
        payer = authority,
        space = 8 + Strategy::INIT_SPACE,
        seeds = [b"strategy", authority.key().as_ref()],
        bump
    )]
    pub strategy: Account<'info, Strategy>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[account]
#[derive(InitSpace)]
pub struct MXE {
    pub authority: Pubkey,    // 32
    pub bump: u8,             // 1
    pub total_computations: u64, // 8
    pub successful_computations: u64, // 8
    pub created_at: i64,      // 8
}

#[account]
#[derive(InitSpace)]
pub struct Strategy {
    pub owner: Pubkey,        // 32
    pub bump: u8,             // 1
    pub total_return: i64,    // 8 (in basis points)
    pub win_rate: u16,        // 2 (in basis points)
    pub total_trades: u32,    // 4
    pub win_trades: u32,      // 4
    pub last_updated: i64,    // 8
}

#[event]
pub struct RSIComputationRequested {
    pub authority: Pubkey,
    pub rsi_period: u8,
    pub rsi_oversold: u8,
    pub rsi_overbought: u8,
    pub timestamp: i64,
}

#[event]
pub struct PositionSizeComputationRequested {
    pub authority: Pubkey,
    pub risk_percentage: u8,
    pub current_price: u64,
    pub timestamp: i64,
}

#[event]
pub struct PerformanceComputationRequested {
    pub authority: Pubkey,
    pub timestamp: i64,
}

#[event]
pub struct StrategyPerformanceUpdated {
    pub strategy: Pubkey,
    pub total_return: i64,
    pub win_rate: u16,
    pub total_trades: u32,
    pub win_trades: u32,
    pub timestamp: i64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Unauthorized access")]
    Unauthorized,
    #[msg("Invalid RSI parameters")]
    InvalidRSIParameters,
    #[msg("Invalid risk percentage")]
    InvalidRiskPercentage,
    #[msg("Computation failed")]
    ComputationFailed,
    #[msg("Strategy not found")]
    StrategyNotFound,
}
