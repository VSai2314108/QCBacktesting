import pandas as pd
import os
import zipfile

def allocation_df_to_stats(df: pd.DataFrame):
    # data frame has columns which are ticker names and values are the allocation weights
    # rows are the dates
    def read_data_from_zip(symbol):
        data_directory = "../data/equity/usa/daily/"
        file_path = os.path.join(data_directory, f"{symbol.lower()}.zip")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            with zip_ref.open(f"{symbol.lower()}.csv") as file:
                df = pd.read_csv(file, header=None, names=["DateTime", "Open", "High", "Low", "Close", "Volume"])
                # Convert DateTime to proper datetime format
                df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y%m%d %H:%M')
                # Convert prices from deci-cents to dollars
                df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']] / 10000
                return df

    equity_df = pd.DataFrame()
    equity_df['DateTime'] = df.index
    equity_df['Equity'] = 100000.0  # Assuming an initial equity of 100

    for symbol, weight in df.iteritems():
        if symbol != 'DateTime':
            symbol_data = read_data_from_zip(symbol)
            equity_df = equity_df.merge(symbol_data[['DateTime', 'Open']], on='DateTime', how='left')
            equity_df[f'Equity_{symbol}'] = equity_df['Equity'] * weight * equity_df[f'Open_{symbol}']

    equity_df['Equity'] = equity_df[equity_df.filter(regex='Equity_').columns].sum(axis=1)
    equity_df = equity_df[['DateTime', 'Equity']]

    return equity_df
