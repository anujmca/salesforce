import pandas as pd
import os

csv_path = r'C:\Projects\GreyChain\ai\prediction\raw data\ML.csv'
if os.path.exists(csv_path):
    try:
        # Load just a few rows
        df = pd.read_csv(csv_path, nrows=5)
        cols_to_check = ['Expected Start Date', 'Expected Close FP', 'SF Close FP', 'Created Date']
        for col in cols_to_check:
            if col in df.columns:
                print(f"\n--- {col} (First 5 values) ---")
                print(df[col])
            else:
                print(f"\nExample val for {col}: Not Found in columns")
    except Exception as e:
        print(f"Error: {e}")
