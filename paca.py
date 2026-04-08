import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = os.getenv('ALPACA_BASE_URL').replace('/v2', '').rstrip('/')

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def scan_and_buy():
    try:
        # 1. Get all tradable stocks
        active_assets = api.list_assets(status='active')
        symbols = [a.symbol for a in active_assets if a.tradable and a.marginable]
        
        # To avoid overloading the API, we'll scan a subset (e.g., first 200) 
        # or you can pass the whole list if you have a paid data plan.
        symbols_to_scan = symbols[:200] 
        
        print(f"Scanning {len(symbols_to_scan)} stocks...")
        
        # 2. Get snapshots for all symbols at once
        snapshots = api.get_snapshots(symbols_to_scan)
        
        for symbol, snapshot in snapshots.items():
            current_price = snapshot.latest_trade.price
            prev_close = snapshot.prev_daily_bar.close
            
            # 3. Apply your Logic:
            # - Price between $10 and $50
            # - Current price is lower than yesterday's close
            if 10 <= current_price <= 50 and current_price < prev_close:
                print(f"MATCH: {symbol} | Now: ${current_price} | Prev: ${prev_close}")
                
                # 4. Place the Buy Order
                api.submit_order(
                    symbol=symbol,
                    qty=1,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"Ordered 1 share of {symbol}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scan_and_buy()
    