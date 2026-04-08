import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load .env for local testing (GitHub ignores this)
load_dotenv()

# 1. Setup Credentials
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets').replace('/v2', '').rstrip('/')

# 2. Connection Safety Check
if not API_KEY or not API_SECRET:
    print(f"ERROR: Credentials missing. Key: {bool(API_KEY)}, Secret: {bool(API_SECRET)}")
    raise ValueError("Check GitHub Secrets and YAML 'env' section.")

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def sell_weak_stocks():
    """Sells positions losing more than 2%"""
    print("Checking for weak positions...")
    positions = api.list_positions()
    for p in positions:
        if float(p.unrealized_plpc) <= -0.02:
            print(f"Selling {p.symbol}: Loss of {float(p.unrealized_plpc)*100:.2f}%")
            api.close_position(p.symbol)

def scan_and_buy():
    """Buys $500 worth of stocks between $10-$50 that are 'red' today"""
    BUDGET_PER_STOCK = 500
    
    try:
        existing_symbols = [p.symbol for p in api.list_positions()]
        assets = api.list_assets(status='active')
        # Scan first 150 tradable stocks not already owned
        symbols = [a.symbol for a in assets if a.tradable and a.marginable and a.symbol not in existing_symbols][:150]
        
        snapshots = api.get_snapshots(symbols)
        
        for symbol, snapshot in snapshots.items():
            if snapshot and snapshot.latest_trade and snapshot.prev_daily_bar:
                price = snapshot.latest_trade.price
                prev_close = snapshot.prev_daily_bar.close
                
                if 10 <= price <= 50 and price < prev_close:
                    qty = int(BUDGET_PER_STOCK // price)
                    if qty > 0:
                        print(f"MATCH: {symbol} @ ${price:.2f}. Ordering {qty} shares.")
                        api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='gtc')
    except Exception as e:
        print(f"Scan error: {e}")

if __name__ == "__main__":
    sell_weak_stocks()
    scan_and_buy()