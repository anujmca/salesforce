import pandas as pd
import os

file_path = r'C:\Projects\GreyChain\ai\prediction\raw data\Comm Rptg _ ERM Opportunity Data for GC _ 01.29.2026.xlsb'

if os.path.exists(file_path):
    print(f"Found file: {file_path}")
    try:
        # Try reading with pandas (requires pyxlsb)
        df = pd.read_excel(file_path, engine='pyxlsb', nrows=5)
        print("Columns found:")
        for col in df.columns:
            print(f"- {col}")
    except ImportError:
        print("Error: pyxlsb library is likely missing.")
    except Exception as e:
        print(f"Error reading excel: {e}")
else:
    print("File not found.")
