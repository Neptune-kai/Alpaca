import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()

# Retrieve credentials from environment variables
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = os.getenv('ALPACA_BASE_URL')

# Initialize the REST API connection
# We check if keys exist to prevent errors before starting
if not API_KEY or not API_SECRET:
    raise ValueError("API Keys not found. Check your .env file!")

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def run_paper_trade():
    try:
        # Verify connection by getting account info
        account = api.get_account()
        print(f"Connection Successful! Buying Power: ${account.buying_power}")

        # Example: Buy 1 share of Tesla (TSLA)
        symbol = 'TSLA'
        print(f"Placing paper trade order for {symbol}...")
        
        api.submit_order(
            symbol=symbol,
            qty=1,
            side='buy',
            type='market',
            time_in_force='day'
        )
        print("Success: Order placed.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_paper_trade()