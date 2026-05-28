import pandas as pd
import json
import os

csv_path = r"C:\Projects\GreyChain\ai\prediction-git\salesforce\quarterly_forecast_predictions.csv"
output_dir = r"C:\Projects\GreyChain\ai\prediction-git\salesforce\dashboard"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

if os.path.exists(csv_path):
    print("Reading prediction data...")
    df = pd.read_csv(csv_path)
    
    # Generate aggregates
    total_unweighted = float(df['Un-Wtd Net Amount'].sum())
    total_expected = float(df['Expected_Revenue'].sum())
    avg_probability = float(df['Win_Probability'].mean())
    
    # Fiscal Period breakdown
    fp_summary = df.groupby('Expected FP')[['Un-Wtd Net Amount', 'Expected_Revenue']].sum().reset_index()
    # Format FP names
    fp_summary['Expected FP'] = fp_summary['Expected FP'].astype(str).apply(lambda x: x.split('.')[0])
    fp_list = fp_summary.to_dict(orient='records')
    
    # Region breakdown
    region_summary = df.groupby('Region')[['Un-Wtd Net Amount', 'Expected_Revenue']].sum().reset_index().to_dict(orient='records')
    
    # Business Unit breakdown
    bu_summary = df.groupby('Business Unit')[['Un-Wtd Net Amount', 'Expected_Revenue']].sum().reset_index().sort_values(by='Expected_Revenue', ascending=False).head(10).to_dict(orient='records')
    
    # Top 100 deals for table display
    top_deals = df.head(100).to_dict(orient='records')
    
    dashboard_data = {
        'total_unweighted': total_unweighted,
        'total_expected': total_expected,
        'avg_probability': avg_probability,
        'fp_summary': fp_list,
        'region_summary': region_summary,
        'bu_summary': bu_summary,
        'top_deals': top_deals
    }
    
    # Export to dashboard/data.js as a global JS object
    js_content = f"const DEFAULT_FORECAST_DATA = {json.dumps(dashboard_data, indent=2)};\n"
    output_path = os.path.join(output_dir, 'data.js')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"Successfully exported live data to: {output_path}")
else:
    print("Prediction CSV not found. Please run the model first.")
