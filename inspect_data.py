import pandas as pd
import os

directory = r'C:\Projects\GreyChain\ai\prediction\raw data'
files = ['Comm Rptg _ ERM Opportunity Data for GC _ 01.29.2026.xlsx', 'ML.xlsx']

for f in files:
    path = os.path.join(directory, f)
    if os.path.exists(path):
        print(f"--- Reading {f} ---")
        try:
            # Read first few rows to infer types if needed, but here just headers
            df = pd.read_excel(path, nrows=2) 
            print(f"Columns: {list(df.columns)}")
            print(f"First row: {df.iloc[0].to_dict()}")
        except Exception as e:
            print(f"Error reading {f}: {e}")
