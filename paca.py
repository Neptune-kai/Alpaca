import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# 1. Load credentials
load_dotenv()

API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets').replace('/v2', '').rstrip('/')

# 2. Initialize API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def sell_weak_stocks():
    """Sells positions that have dropped more than 2%."""
    print("Checking for weak positions to sell...")
    positions = api.list_positions()
    for p in positions:
        # unrealized_plpc is the profit/loss percentage
        if float(p.unrealized_plpc) <= -0.02:
            print(f"Selling {p.symbol}: Loss of {float(p.unrealized_plpc)*100:.2f}%")
            api.close_position(p.symbol)

def scan_and_buy():
    """Buys multiple shares of stocks between $10-$50 that are cheaper than yesterday."""
    print("Scanning for new buying opportunities...")
    
    # Configuration
    BUDGET_PER_STOCK = 500  # Total dollars to spend per stock found
    SCAN_LIMIT = 200        # Number of stocks to check
    
    try:
        # Get existing positions to avoid double-buying
        existing_symbols = [p.symbol for p in api.list_positions()]
        
        # Get active tradable stocks
        assets = api.list_assets(status='active')
        symbols = [a.symbol for a in assets if a.tradable and a.marginable and a.symbol not in existing_symbols]
        
        # Pull data for the first chunk of symbols
        batch = symbols[:SCAN_LIMIT]
        snapshots = api.get_snapshots(batch)
        
        for symbol, snapshot in snapshots.items():
            if snapshot and snapshot.latest_trade and snapshot.prev_daily_bar:
                current_price = snapshot.latest_trade.price
                prev_close = snapshot.prev_daily_bar.close
                
                # Logic: $10-$50 and cheaper than yesterday
                if 10 <= current_price <= 50 and current_price < prev_close:
                    qty = int(BUDGET_PER_STOCK // current_price)
                    
                    if qty > 0:
                        print(f"MATCH: {symbol} at ${current_price:.2f} (Yesterday: ${prev_close:.2f})")
                        api.submit_order(
                            symbol=symbol,
                            qty=qty,
                            side='buy',
                            type='market',
                            time_in_force='gtc'
                        )
                        print(f"✅ Order placed for {qty} shares of {symbol}")

    except Exception as e:
        print(f"Error during scan/buy: {e}")

if __name__ == "__main__":
    # First, clean house (sell losers)
    sell_weak_stocks()
    # Second, find new opportunities
    scan_and_buy()
    print("Cycle complete.")