import pandas as pd
import os
import zipfile
import numpy as np
from matplotlib import pyplot as plt
def read_data_from_zip(symbol):
    data_directory = "../data/equity/usa/daily/"
    file_path = os.path.join(data_directory, f"{symbol.lower()}.zip")
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        with zip_ref.open(f"{symbol.lower()}.csv") as file:
            df = pd.read_csv(file, header=None, names=["DateTime", "Open", "High", "Low", "Close", "Volume"])
            # Convert DateTime to proper datetime format
            df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y%m%d %H:%M')
            # if the time is 00:00, set it to 16:00 and reduce the date by 1 - this is to account for both formats that quant connect runs in 
            df['DateTime'] = df['DateTime'].apply(lambda x: x.replace(hour=16, minute=0) - pd.DateOffset(days=1) if x.hour == 0 else x)
            # convert back to datetime
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            # set the index as date time
            df.set_index('DateTime', inplace=True)
            # Convert prices from deci-cents to dollars
            df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']] / 10000
            # sort so oldest dates are first
            df = df.sort_values(by='DateTime', ascending=True)
            return df
        

def build_stats_from_allocations(csv_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)
    df = df.set_index('Date')
    # remove the time from the index to ensure matching is done correctly
    df.index = pd.to_datetime(df.index).date
    
    # Read historical price data for all the tickers
    tickers = df.columns
    price_data = {ticker: read_data_from_zip(ticker) for ticker in tickers}
    
    # Aligning price data with the allocation data (assuming they have the same dates)
    for ticker in tickers:
        # remove times from the index to ensure matching is done correctly
        price_data[ticker].index = pd.to_datetime(price_data[ticker].index).date
        price_data[ticker] = price_data[ticker].loc[df.index]
        price_data[ticker]['Daily_Return%'] = price_data[ticker]['Open'].pct_change() * 100
    
    # sort the data frame so that the oldest data is first
    portfolio_returns = pd.Series(np.zeros(len(df.index)), index=df.index)
    for ticker in tickers:
        portfolio_returns += (df[ticker].shift(-1)) * ((price_data[ticker]['Daily_Return%'])/100)
    
    # Rolling 20-day Sharpe ratio
    rolling_sharpe_ratio = (portfolio_returns.rolling(window=20).mean() / 
                            portfolio_returns.rolling(window=20).std()) * np.sqrt(252)
    
    # Rolling 20-day return
    rolling_return = portfolio_returns.rolling(window=20).sum() * 100

    # Compute drawdown & cum returns
    cumulative_returns = (1 + portfolio_returns).cumprod()
    drawdown = (cumulative_returns / cumulative_returns.cummax()) - 1
    cumulative_returns = cumulative_returns - 1
    
    # adjust portfolio returns to percent
    portfolio_returns = portfolio_returns * 100

    # Combine all metrics into a single DataFrame
    stats_df = pd.DataFrame({
        'Portfolio Return Daily': portfolio_returns,
        'Drawdown %': drawdown,
        'Cumulative Return %': cumulative_returns,
        'Rolling Return % 20D': rolling_return,
        'Rolling Sharpe Ratio 20D': rolling_sharpe_ratio
    })
    stats_df.index.name = 'Date'
    
    # Write the resulting DataFrame to a CSV file
    output_file = os.path.splitext(csv_file)[0] + "_stats.csv"
    stats_df.to_csv(output_file)

    print(f"Statistics computed and written to {output_file}")
    
    # copy the index column to a new column called Date
    stats_df['Date'] = stats_df.index
    
    # build charts 
    plt.close('all')
    # Daily return chart - bar chart
    stats_df.plot(x='Date', y='Portfolio Return Daily', title='Portfolio Daily Return', kind='bar')
    plt.savefig(os.path.splitext(csv_file)[0] + "_daily_return.png")
    
    # Cumulative return chart
    stats_df.plot(x='Date', y='Cumulative Return %', title='Portfolio Cumulative Return')
    plt.savefig(os.path.splitext(csv_file)[0] + "_cumulative_return.png")
    
    # Drawdown chart
    stats_df.plot(x='Date', y='Drawdown %', title='Portfolio Drawdown')
    plt.savefig(os.path.splitext(csv_file)[0] + "_drawdown.png")
    
    # Rolling return chart - bar chart
    stats_df.plot(x='Date', y='Rolling Return % 20D', title='Portfolio Rolling Return 20D', kind='bar')
    plt.savefig(os.path.splitext(csv_file)[0] + "_rolling_return.png")
    
    # Rolling Sharpe ratio chart
    stats_df.plot(x='Date', y='Rolling Sharpe Ratio 20D', title='Portfolio Rolling Sharpe Ratio 20D')
    plt.savefig(os.path.splitext(csv_file)[0] + "_rolling_sharpe_ratio.png")
    
    
    
    

def build_stats_from_backtest(backtest_name):
        parent_dir = "/Users/vsai23/Workspace/MBQC2/QCBacktesting/backtests"
        backtest_dir = f"{parent_dir}/{backtest_name}"
        
        # build a list of all .csv files in the backtest directory recursively
        csv_files = []
        for root, _, files in os.walk(backtest_dir):
            for file in files:
                if file.endswith(".csv"):
                    csv_files.append(os.path.join(root, file))
        
        for file in csv_files:
            build_stats_from_allocations(file)