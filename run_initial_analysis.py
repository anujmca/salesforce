import pandas as pd
import numpy as np
import os

file_path = r"C:\Projects\GreyChain\ai\prediction-git\salesforce\raw data\20260527\Comm Rptg _ ERM Opportunity Data for GC _ 05.25.2026.xlsb"

if not os.path.exists(file_path):
    print("Error: File not found.")
    exit(1)

print("Loading dataset...")
df = pd.read_excel(file_path, sheet_name='ERM_Pipeline_Data', engine='pyxlsb')
print(f"Loaded {len(df)} rows.")

# 1. Standardize and parse dates
# Convert 'Month Date' to datetime for sorting
df['Month_Date_DT'] = pd.to_datetime(df['Month Date'])
snapshot_dates = sorted(df['Month_Date_DT'].unique())
print(f"Snapshots found: {[d.strftime('%Y-%m-%d') for d in snapshot_dates]}")

# Ensure clean numeric amounts
df['Un-Wtd Net Amount'] = pd.to_numeric(df['Un-Wtd Net Amount'], errors='coerce').fillna(0)
df['Weighted Net Amount'] = pd.to_numeric(df['Weighted Net Amount'], errors='coerce').fillna(0)

# 2. Pipeline Size over Time Analysis
print("\n--- PIPELINE SIZE OVER TIME ---")
pipeline_summary = []
for d in snapshot_dates:
    snap_df = df[df['Month_Date_DT'] == d]
    num_deals = snap_df['Opportunity Number'].nunique() # unique deals
    total_val = snap_df['Un-Wtd Net Amount'].sum()
    weighted_val = snap_df['Weighted Net Amount'].sum()
    pipeline_summary.append({
        'Snapshot Date': d.strftime('%Y-%m-%d'),
        'Unique Opportunity Count': num_deals,
        'Total Pipeline Value ($)': total_val,
        'Weighted Pipeline Value ($)': weighted_val
    })
df_summary = pd.DataFrame(pipeline_summary)
print(df_summary.to_string(index=False))

# Save summary to csv
df_summary.to_csv('pipeline_size_summary.csv', index=False)

# 3. Profiling Key Columns (Region, Business Unit, Country/Entity, Service Group, Core Industry, Client)
print("\n--- PROFILING PRIMARY COLUMNS ---")
primary_cols = ['Region', 'Business Unit', 'Country/Entity', 'Service Group', 'Core Industry', 'Client']
for col in primary_cols:
    if col in df.columns:
        null_count = df[col].isnull().sum() + (df[col].astype(str).str.strip() == '').sum()
        unique_count = df[col].nunique()
        print(f"\nCol: '{col}' | Missing: {null_count} ({null_count/len(df)*100:.2f}%) | Unique: {unique_count}")
        print("Top 5 Values:")
        top5 = df[col].value_counts(dropna=False).head(5)
        for val, count in top5.items():
            print(f"  - {val}: {count} ({count/len(df)*100:.1f}%)")

# 4. Tracking Transitions and Disappearances between consecutive snapshots
print("\n--- DEAL TRANSITIONS BETWEEN SNAPSHOTS ---")

# We want to compare snapshot T to snapshot T+1
for i in range(len(snapshot_dates) - 1):
    t_date = snapshot_dates[i]
    t1_date = snapshot_dates[i+1]
    
    t_str = t_date.strftime('%Y-%m-%d')
    t1_str = t1_date.strftime('%Y-%m-%d')
    
    print(f"\nAnalyzing transitions: {t_str} -> {t1_str}")
    
    # Get snapshot dfs
    t_df = df[df['Month_Date_DT'] == t_date].copy()
    t1_df = df[df['Month_Date_DT'] == t1_date].copy()
    
    # De-duplicate snapshots to get unique opportunities
    # For stage, take the max stage (furthest advanced) to represent the deal
    t_opps_stage = t_df.groupby('Opportunity Number')['Stage'].max()
    t1_opps_stage = t1_df.groupby('Opportunity Number')['Stage'].max()
    
    t_opp_ids = set(t_opps_stage.index)
    t1_opp_ids = set(t1_opps_stage.index)
    
    common_opps = t_opp_ids.intersection(t1_opp_ids)
    disappeared_opps = t_opp_ids.difference(t1_opp_ids)
    new_opps = t1_opp_ids.difference(t_opp_ids)
    
    print(f"  Active unique deals in {t_str}: {len(t_opp_ids)}")
    print(f"  Active unique deals in {t1_str}: {len(t1_opp_ids)}")
    print(f"  Carried Over: {len(common_opps)} ({len(common_opps)/len(t_opp_ids)*100:.1f}% of previous)")
    print(f"  Disappeared (Implied Closed): {len(disappeared_opps)} ({len(disappeared_opps)/len(t_opp_ids)*100:.1f}% of previous)")
    print(f"  New Deals Added: {len(new_opps)}")
    
    # Analyze stage progression for carried over deals
    def stage_to_num(stage_str):
        if '1.' in str(stage_str): return 1
        if '2.' in str(stage_str): return 2
        if '3.' in str(stage_str): return 3
        if '4.' in str(stage_str): return 4
        return 0
        
    stages_t = t_opps_stage.loc[list(common_opps)].apply(stage_to_num)
    stages_t1 = t1_opps_stage.loc[list(common_opps)].apply(stage_to_num)
    
    # Sort series to ensure aligned indexes
    stages_t = stages_t.sort_index()
    stages_t1 = stages_t1.sort_index()
    
    advanced = (stages_t1 > stages_t).sum()
    stagnant = (stages_t1 == stages_t).sum()
    slipped = (stages_t1 < stages_t).sum()
    
    print(f"  Of carried over deals:")
    print(f"    - Advanced Stage: {advanced} ({advanced/len(common_opps)*100:.1f}%)")
    print(f"    - Stagnant Stage: {stagnant} ({stagnant/len(common_opps)*100:.1f}%)")
    print(f"    - Slipped Stage: {slipped} ({slipped/len(common_opps)*100:.1f}%)")
    
    # Disappeared deals analysis by their last stage in T
    print(f"  Disappearance (Close) Rate by Stage in {t_str}:")
    t_stage_counts = t_opps_stage.value_counts()
    disappeared_stages = t_opps_stage.loc[list(disappeared_opps)].value_counts()
    for stage in sorted(t_stage_counts.index):
        total = t_stage_counts.get(stage, 0)
        dis_count = disappeared_stages.get(stage, 0)
        rate = dis_count / total * 100 if total > 0 else 0
        print(f"    - {stage}: {dis_count}/{total} disappeared ({rate:.1f}%)")

print("\n--- ANALYSIS COMPLETED ---")
