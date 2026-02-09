import pandas as pd
import os

file_path = r'C:\Projects\GreyChain\ai\prediction\raw data\Comm Rptg _ ERM Opportunity Data for GC _ 01.29.2026.xlsb'

if os.path.exists(file_path):
    try:
        xls = pd.ExcelFile(file_path, engine='pyxlsb')
        print("Sheets found:", xls.sheet_names)
    except Exception as e:
        print(f"Error reading sheets: {e}")
else:
    print("File not found.")
