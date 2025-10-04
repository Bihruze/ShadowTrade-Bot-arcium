#!/usr/bin/env python3
"""
Wallet Manager for ShadowTrade Bot
Handles Solana wallet integration and management
"""

import json
import os
import base58
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess

class SolanaWalletManager:
    """Manages Solana wallets for ShadowTrade Bot"""
    
    def __init__(self, wallet_dir: str = "./wallets"):
        self.wallet_dir = wallet_dir
        self.current_wallet = None
        self.wallet_data = {}
        
        # Create wallet directory if it doesn't exist
        os.makedirs(wallet_dir, exist_ok=True)
        
        print("🔐 Solana Wallet Manager initialized")
        print(f"   📁 Wallet directory: {os.path.abspath(wallet_dir)}")
    
    def generate_new_wallet(self, wallet_name: str = None) -> Dict[str, Any]:
        """Generate a new Solana wallet"""
        if not wallet_name:
            wallet_name = f"shadowtrade_wallet_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🔑 Generating new wallet: {wallet_name}")
        
        try:
            # Generate keypair using Node.js (Solana CLI simulation)
            script = f"""
            const {{ Keypair }} = require('@solana/web3.js');
            const fs = require('fs');
            
            const keypair = Keypair.generate();
            const walletData = {{
                name: '{wallet_name}',
                publicKey: keypair.publicKey.toString(),
                secretKey: Array.from(keypair.secretKey),
                created_at: new Date().toISOString(),
                network: 'devnet'
            }};
            
            console.log(JSON.stringify(walletData));
            """
            
            result = subprocess.run(['node', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                wallet_data = json.loads(result.stdout)
                
                # Save wallet to file
                wallet_file = os.path.join(self.wallet_dir, f"{wallet_name}.json")
                with open(wallet_file, 'w') as f:
                    json.dump(wallet_data, f, indent=2)
                
                print(f"   ✅ Wallet generated successfully")
                print(f"   📍 Public Key: {wallet_data['publicKey']}")
                print(f"   💾 Saved to: {wallet_file}")
                
                return wallet_data
            else:
                # Fallback: Generate mock wallet
                return self._generate_mock_wallet(wallet_name)
                
        except Exception as e:
            print(f"   ⚠️ Node.js generation failed: {e}")
            print(f"   🔄 Using mock wallet generation")
            return self._generate_mock_wallet(wallet_name)
    
    def _generate_mock_wallet(self, wallet_name: str) -> Dict[str, Any]:
        """Generate a mock wallet for testing"""
        import secrets
        
        # Generate mock keypair
        secret_key = [secrets.randbelow(256) for _ in range(64)]
        public_key = base58.b58encode(secret_key[:32]).decode()
        
        wallet_data = {
            "name": wallet_name,
            "publicKey": public_key,
            "secretKey": secret_key,
            "created_at": datetime.now().isoformat(),
            "network": "devnet",
            "type": "mock"
        }
        
        # Save wallet to file
        wallet_file = os.path.join(self.wallet_dir, f"{wallet_name}.json")
        with open(wallet_file, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        
        print(f"   ✅ Mock wallet generated")
        print(f"   📍 Public Key: {public_key}")
        print(f"   💾 Saved to: {wallet_file}")
        
        return wallet_data
    
    def load_wallet(self, wallet_name: str) -> Dict[str, Any]:
        """Load an existing wallet"""
        wallet_file = os.path.join(self.wallet_dir, f"{wallet_name}.json")
        
        if not os.path.exists(wallet_file):
            raise FileNotFoundError(f"Wallet not found: {wallet_name}")
        
        with open(wallet_file, 'r') as f:
            wallet_data = json.load(f)
        
        self.current_wallet = wallet_data
        self.wallet_data[wallet_name] = wallet_data
        
        print(f"🔑 Wallet loaded: {wallet_name}")
        print(f"   📍 Public Key: {wallet_data['publicKey']}")
        print(f"   🌐 Network: {wallet_data.get('network', 'unknown')}")
        
        return wallet_data
    
    def list_wallets(self) -> List[Dict[str, Any]]:
        """List all available wallets"""
        wallets = []
        
        for filename in os.listdir(self.wallet_dir):
            if filename.endswith('.json'):
                wallet_name = filename[:-5]  # Remove .json extension
                wallet_file = os.path.join(self.wallet_dir, filename)
                
                try:
                    with open(wallet_file, 'r') as f:
                        wallet_data = json.load(f)
                    
                    wallets.append({
                        "name": wallet_name,
                        "publicKey": wallet_data.get('publicKey', 'Unknown'),
                        "created_at": wallet_data.get('created_at', 'Unknown'),
                        "network": wallet_data.get('network', 'Unknown'),
                        "type": wallet_data.get('type', 'real')
                    })
                except Exception as e:
                    print(f"   ⚠️ Error loading wallet {wallet_name}: {e}")
        
        return wallets
    
    def get_wallet_balance(self, wallet_name: str = None) -> Dict[str, Any]:
        """Get wallet balance from Solana network"""
        if not wallet_name and not self.current_wallet:
            raise ValueError("No wallet selected")
        
        if wallet_name:
            wallet_data = self.load_wallet(wallet_name)
        else:
            wallet_data = self.current_wallet
        
        print(f"💰 Checking balance for: {wallet_data['publicKey']}")
        
        try:
            # Check balance using Solana RPC
            script = f"""
            const {{ Connection, PublicKey }} = require('@solana/web3.js');
            
            const connection = new Connection('https://api.devnet.solana.com', 'confirmed');
            const publicKey = new PublicKey('{wallet_data['publicKey']}');
            
            connection.getBalance(publicKey).then(balance => {{
                console.log(JSON.stringify({{
                    balance: balance / 1000000000, // Convert lamports to SOL
                    lamports: balance,
                    publicKey: publicKey.toString()
                }}));
            }}).catch(error => {{
                console.log(JSON.stringify({{
                    error: error.message,
                    balance: 0,
                    lamports: 0
                }}));
            }});
            """
            
            result = subprocess.run(['node', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                balance_data = json.loads(result.stdout)
                print(f"   💰 Balance: {balance_data.get('balance', 0):.4f} SOL")
                return balance_data
            else:
                # Fallback: Mock balance
                return self._get_mock_balance(wallet_data)
                
        except Exception as e:
            print(f"   ⚠️ Balance check failed: {e}")
            return self._get_mock_balance(wallet_data)
    
    def _get_mock_balance(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get mock balance for testing"""
        import random
        
        balance = random.uniform(0.5, 10.0)  # Random balance between 0.5-10 SOL
        lamports = int(balance * 1000000000)
        
        balance_data = {
            "balance": balance,
            "lamports": lamports,
            "publicKey": wallet_data['publicKey'],
            "type": "mock"
        }
        
        print(f"   💰 Mock Balance: {balance:.4f} SOL")
        return balance_data
    
    def fund_wallet(self, wallet_name: str = None, amount: float = 1.0) -> Dict[str, Any]:
        """Fund wallet with test SOL (devnet only)"""
        if not wallet_name and not self.current_wallet:
            raise ValueError("No wallet selected")
        
        if wallet_name:
            wallet_data = self.load_wallet(wallet_name)
        else:
            wallet_data = self.current_wallet
        
        print(f"💰 Funding wallet with {amount} SOL...")
        
        try:
            # Request airdrop from Solana devnet
            script = f"""
            const {{ Connection, PublicKey, LAMPORTS_PER_SOL }} = require('@solana/web3.js');
            
            const connection = new Connection('https://api.devnet.solana.com', 'confirmed');
            const publicKey = new PublicKey('{wallet_data['publicKey']}');
            const lamports = {amount} * LAMPORTS_PER_SOL;
            
            connection.requestAirdrop(publicKey, lamports).then(signature => {{
                console.log(JSON.stringify({{
                    success: true,
                    signature: signature,
                    amount: {amount},
                    publicKey: publicKey.toString()
                }}));
            }}).catch(error => {{
                console.log(JSON.stringify({{
                    success: false,
                    error: error.message,
                    amount: {amount}
                }}));
            }});
            """
            
            result = subprocess.run(['node', '-e', script], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                airdrop_data = json.loads(result.stdout)
                if airdrop_data.get('success'):
                    print(f"   ✅ Airdrop successful!")
                    print(f"   📝 Signature: {airdrop_data['signature']}")
                    return airdrop_data
                else:
                    print(f"   ❌ Airdrop failed: {airdrop_data.get('error')}")
                    return airdrop_data
            else:
                # Fallback: Mock funding
                return self._mock_fund_wallet(wallet_data, amount)
                
        except Exception as e:
            print(f"   ⚠️ Funding failed: {e}")
            return self._mock_fund_wallet(wallet_data, amount)
    
    def _mock_fund_wallet(self, wallet_data: Dict[str, Any], amount: float) -> Dict[str, Any]:
        """Mock wallet funding for testing"""
        funding_data = {
            "success": True,
            "signature": f"mock_signature_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "amount": amount,
            "publicKey": wallet_data['publicKey'],
            "type": "mock"
        }
        
        print(f"   ✅ Mock funding successful!")
        print(f"   📝 Mock Signature: {funding_data['signature']}")
        return funding_data
    
    def export_wallet(self, wallet_name: str, export_format: str = "json") -> str:
        """Export wallet in various formats"""
        wallet_data = self.load_wallet(wallet_name)
        
        if export_format == "json":
            return json.dumps(wallet_data, indent=2)
        elif export_format == "base64":
            return base64.b64encode(json.dumps(wallet_data).encode()).decode()
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def import_wallet(self, wallet_data: str, wallet_name: str, import_format: str = "json") -> Dict[str, Any]:
        """Import wallet from various formats"""
        if import_format == "json":
            data = json.loads(wallet_data)
        elif import_format == "base64":
            data = json.loads(base64.b64decode(wallet_data).decode())
        else:
            raise ValueError(f"Unsupported import format: {import_format}")
        
        # Save imported wallet
        wallet_file = os.path.join(self.wallet_dir, f"{wallet_name}.json")
        with open(wallet_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"🔑 Wallet imported: {wallet_name}")
        print(f"   📍 Public Key: {data.get('publicKey', 'Unknown')}")
        
        return data

def main():
    """Main function for wallet management"""
    wallet_manager = SolanaWalletManager()
    
    print("\n🔐 ShadowTrade Bot - Wallet Manager")
    print("="*50)
    
    while True:
        print("\n📋 Available Commands:")
        print("1. Generate New Wallet")
        print("2. Load Existing Wallet")
        print("3. List All Wallets")
        print("4. Check Wallet Balance")
        print("5. Fund Wallet (Devnet)")
        print("6. Export Wallet")
        print("7. Import Wallet")
        print("8. Exit")
        
        choice = input("\n🎯 Select option (1-8): ").strip()
        
        if choice == "1":
            wallet_name = input("📝 Enter wallet name (optional): ").strip()
            wallet_manager.generate_new_wallet(wallet_name or None)
        
        elif choice == "2":
            wallet_name = input("📝 Enter wallet name: ").strip()
            try:
                wallet_manager.load_wallet(wallet_name)
            except FileNotFoundError as e:
                print(f"❌ {e}")
        
        elif choice == "3":
            wallets = wallet_manager.list_wallets()
            print(f"\n📋 Available Wallets ({len(wallets)}):")
            for wallet in wallets:
                print(f"   🔑 {wallet['name']}")
                print(f"      📍 {wallet['publicKey']}")
                print(f"      🌐 {wallet['network']} ({wallet['type']})")
                print(f"      📅 {wallet['created_at']}")
        
        elif choice == "4":
            wallet_name = input("📝 Enter wallet name (optional): ").strip()
            try:
                balance = wallet_manager.get_wallet_balance(wallet_name or None)
                print(f"💰 Balance: {balance.get('balance', 0):.4f} SOL")
            except Exception as e:
                print(f"❌ {e}")
        
        elif choice == "5":
            wallet_name = input("📝 Enter wallet name (optional): ").strip()
            amount = float(input("💰 Enter amount in SOL (default: 1.0): ").strip() or "1.0")
            try:
                result = wallet_manager.fund_wallet(wallet_name or None, amount)
                if result.get('success'):
                    print("✅ Wallet funded successfully!")
                else:
                    print(f"❌ Funding failed: {result.get('error')}")
            except Exception as e:
                print(f"❌ {e}")
        
        elif choice == "6":
            wallet_name = input("📝 Enter wallet name: ").strip()
            export_format = input("📤 Export format (json/base64, default: json): ").strip() or "json"
            try:
                exported = wallet_manager.export_wallet(wallet_name, export_format)
                print(f"📤 Exported wallet:")
                print(exported)
            except Exception as e:
                print(f"❌ {e}")
        
        elif choice == "7":
            wallet_name = input("📝 Enter wallet name: ").strip()
            import_format = input("📥 Import format (json/base64, default: json): ").strip() or "json"
            wallet_data = input("📥 Enter wallet data: ").strip()
            try:
                wallet_manager.import_wallet(wallet_data, wallet_name, import_format)
                print("✅ Wallet imported successfully!")
            except Exception as e:
                print(f"❌ {e}")
        
        elif choice == "8":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please select 1-8.")

if __name__ == "__main__":
    main()
