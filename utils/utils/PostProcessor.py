import pandas as pd
import os
import zipfile
import json
from matplotlib import pyplot as plt

# Initialize starting equity
initial_equity = 100000

# Path to the data directory
data_directory = "../data/equity/usa/daily/"
path_to_backtest = "/Users/vsai23/Workspace/MBQC2/QCBacktesting/backtests/2024-07-26_10-37-40/1905905250-order-events.json"
with open(path_to_backtest) as file:
    orders = json.load(file)

# Function to read data from a zip file and return a DataFrame
def read_data_from_zip(symbol):
    file_path = os.path.join(data_directory, f"{symbol.lower()}.zip")
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        with zip_ref.open(f"{symbol.lower()}.csv") as file:
            df = pd.read_csv(file, header=None, names=["DateTime", "Open", "High", "Low", "Close", "Volume"])
            # Convert DateTime to proper datetime format
            df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y%m%d %H:%M')
            # Convert prices from deci-cents to dollars
            df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']] / 10000
            return df

def process_orders(orders):
    orders_df = pd.DataFrame(orders)
    orders_df['DateTime'] = pd.to_datetime(orders_df['time'], unit='s')
    orders_df = orders_df.sort_values(by='DateTime')

    # Initialize starting values
    cash = initial_equity
    portfolio = {}

    # Create a list to hold the equity values over time
    equity_values = []

    # Get the unique trading days from the data
    all_trading_days = pd.date_range(orders_df['DateTime'].min().date(), orders_df['DateTime'].max().date(), freq='B')
    all_trading_days = [date.date() for date in all_trading_days]
    orders_df.set_index('DateTime', inplace=True)
    
    # ensure all dates in the orders_df are in the all_trading_days if not print them and add them
    for date in orders_df.index:
        if date.date() not in all_trading_days:
            print(date.date())
            all_trading_days = all_trading_days.append(pd.DatetimeIndex([date.date()]))

    for date in all_trading_days:
        print(date)
        # Filter orders up to the current date
        day_orders = orders_df.loc[orders_df.index.date == date]

        # Process the day's orders
        for index, row in day_orders.iterrows():
            if row['status'] == 'filled':
                symbol = row['symbolPermtick']
                quantity = row['fillQuantity']
                price = row['fillPrice']

                cost = quantity * price
                cash -= cost
                if symbol in portfolio:
                    portfolio[symbol] += quantity
                else:
                    portfolio[symbol] = quantity

        # Get the latest price for each symbol in the portfolio
        equity_value = 0
        print(portfolio)
        for sym in portfolio:
            df = read_data_from_zip(sym)
            # Ensure we have data for the date and after
            df = df[df['DateTime'].dt.date <= date]
            if not df.empty:
                last_close = df.iloc[-1]['Close']
                equity_value += portfolio[sym] * last_close

        account_value = cash + equity_value

        equity_values.append({'Date': date, 'Cash': cash, 'Equity': equity_value, 'Account': account_value})

    # Create a DataFrame for equity values
    equity_df = pd.DataFrame(equity_values)

    # STEP 1 EQUITY CURVE
    equity_df.plot(x='Date', y=['Account'], title='Equity Curve')
    plt.savefig(f"{path_to_backtest.replace('order-events.json', 'equity_curve.png')}")
    
    # STEP 2 PERCENTAGE CURVE
    equity_df['Percentage'] = equity_df['Account'] / initial_equity
    
    equity_df.plot(x='Date', y=['Percentage'], title='Percentage Curve')
    plt.savefig(f"{path_to_backtest.replace('order-events.json', 'percentage_curve.png')}")
    
    # STEP 3 SAVE DRAWDOWN AND DRAWDOWN PERCENTAGE - 2 seperate curves
    equity_df['Drawdown'] = equity_df['Account'].cummax() - equity_df['Account']
    equity_df['DrawdownPercentage'] = equity_df['Drawdown'] / equity_df['Account'].cummax()
    
    equity_df.plot(x='Date', y=['Drawdown'], title='Drawdown Curve')
    plt.savefig(f"{path_to_backtest.replace('order-events.json', 'drawdown_curve.png')}")
    
    equity_df.plot(x='Date', y=['DrawdownPercentage'], title='Drawdown Percentage Curve')
    plt.savefig(f"{path_to_backtest.replace('order-events.json', 'drawdown_percentage_curve.png')}")
    
    # STEP 4 - MONTHLY RETURNS
    equity_df['Date'] = pd.to_datetime(equity_df['Date'])  # Ensure Date is in datetime format
    equity_df['Month'] = equity_df['Date'].dt.to_period('M')
    monthly_returns = equity_df.groupby('Month')['Account'].last().pct_change()
    monthly_returns.plot(kind='bar', title='Monthly Returns')
    plt.savefig(f"{path_to_backtest.replace('order-events.json', 'monthly_returns.png')}")    
    

if __name__ == "__main__":
    process_orders(orders)
