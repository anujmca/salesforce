import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

new_file = r"C:\Projects\GreyChain\ai\prediction-git\salesforce\raw data\20260527\Comm Rptg _ ERM Opportunity Data for GC _ 05.25.2026.xlsb"
ml_csv = r"C:\Projects\GreyChain\ai\prediction-git\salesforce\raw data\ML.csv"

if not (os.path.exists(new_file) and os.path.exists(ml_csv)):
    print("Error: Input files not found.")
    exit(1)

print("1. Loading datasets...")
df_snap = pd.read_excel(new_file, sheet_name='ERM_Pipeline_Data', engine='pyxlsb')
df_snap['Month_Date_DT'] = pd.to_datetime(df_snap['Month Date'])

df_ml = pd.read_csv(ml_csv, low_memory=False)

# Clean amounts
df_snap['Un-Wtd Net Amount'] = pd.to_numeric(df_snap['Un-Wtd Net Amount'], errors='coerce').fillna(0)
df_snap['Weighted Net Amount'] = pd.to_numeric(df_snap['Weighted Net Amount'], errors='coerce').fillna(0)

# Sort chronologically to engineer features correctly
df_snap = df_snap.sort_values(by=['Opportunity Number', 'Month_Date_DT'])

print("2. Engineering snapshot progression features...")
# De-duplicate snapshots for the same opportunity in the same month (taking the max/peak stage)
df_snap_clean = df_snap.groupby(['Opportunity Number', 'Month_Date_DT']).first().reset_index()

# Helper stage to numeric
def stage_to_num(stage_str):
    if '1.' in str(stage_str): return 1
    if '2.' in str(stage_str): return 2
    if '3.' in str(stage_str): return 3
    if '4.' in str(stage_str): return 4
    return 0

df_snap_clean['Stage_Num'] = df_snap_clean['Stage'].apply(stage_to_num)

# Group by Opportunity Number and calculate progression metrics
grouped = df_snap_clean.groupby('Opportunity Number')

# Stagnation count (months in stage)
stagnant_list = []
prev_opp = None
prev_stage = None
stag_count = 0

for idx, row in df_snap_clean.iterrows():
    curr_opp = row['Opportunity Number']
    curr_stage = row['Stage_Num']
    
    if curr_opp != prev_opp:
        stag_count = 0
    else:
        if curr_stage == prev_stage:
            stag_count += 1
        else:
            stag_count = 0
            
    stagnant_list.append(stag_count)
    prev_opp = curr_opp
    prev_stage = curr_stage

df_snap_clean['stagnant_months'] = stagnant_list

# Stage change dynamics (advancement / slippage)
df_snap_clean['stage_diff'] = grouped['Stage_Num'].diff().fillna(0)
df_snap_clean['stage_advanced'] = (df_snap_clean['stage_diff'] > 0).astype(int)
df_snap_clean['stage_slipped'] = (df_snap_clean['stage_diff'] < 0).astype(int)
df_snap_clean['amount_change'] = grouped['Un-Wtd Net Amount'].diff().fillna(0)

print("3. Building Training Dataset (Cross-Referencing outcomes)...")
# Filter opportunities with outcomes recorded in ML.csv
df_ml_outcomes = df_ml[['Opportunity Number', 'Stage', 'IsWon', 'IsClosed']].copy()
# Remove duplicate opportunities from historical file to avoid multiple matches
df_ml_outcomes = df_ml_outcomes.drop_duplicates(subset=['Opportunity Number'])

# Map final closed status from ML.csv
df_merged = pd.merge(df_snap_clean, df_ml_outcomes, on='Opportunity Number', how='inner', suffixes=('', '_final'))

# Labeled training set = snapshots of opportunities that ultimately closed
# Because IsClosed only exists in df_ml_outcomes, it keeps its original name in df_merged
closed_mask = df_merged['IsClosed'].astype(str).str.lower().isin(['true', '1', 'yes'])
df_train_full = df_merged[closed_mask].copy()

# Outcome Target: IsWon = 1, Lost/Abandoned = 0
# IsWon also keeps its original name in df_merged
df_train_full['IsWon_Target'] = df_train_full['IsWon'].astype(str).apply(lambda x: 1 if x.lower() in ['1', 'true', 'yes', 'won'] else 0)

print(f"Total labeled snapshot training rows: {len(df_train_full)}")
print(f"Closed Won snapshots: {df_train_full['IsWon_Target'].sum()} | Closed Lost/Abandoned: {len(df_train_full) - df_train_full['IsWon_Target'].sum()}")

# 4. Preparing Prediction Set (Latest snapshot - Active Pipeline)
latest_date = df_snap_clean['Month_Date_DT'].max()
df_active = df_snap_clean[df_snap_clean['Month_Date_DT'] == latest_date].copy()

# Exclude deals that are already marked closed in ML.csv
closed_opp_ids = set(df_ml_outcomes[df_ml_outcomes['IsClosed'].astype(str).str.lower().isin(['true', '1', 'yes'])]['Opportunity Number'])
df_active = df_active[~df_active['Opportunity Number'].isin(closed_opp_ids)].copy()
print(f"Active opportunities in May snapshot for prediction: {len(df_active)}")

# 5. ML Modeling Pipeline
features = [
    'Region', 'Business Unit', 'Country/Entity', 'Service Group', 'Core Industry', 'Client',
    'stagnant_months', 'stage_advanced', 'stage_slipped', 'amount_change', 'Stage_Num'
]

# Handle Categorical Encoding and Imputations
df_train_full[features] = df_train_full[features].fillna('Unknown')
df_active[features] = df_active[features].fillna('Unknown')

# Standardize column types to string for label encoders
cat_cols = ['Region', 'Business Unit', 'Country/Entity', 'Service Group', 'Core Industry', 'Client']
encoders = {}

for col in cat_cols:
    le = LabelEncoder()
    # Fit encoder on both train and active sets to see all potential labels
    combined_labels = pd.concat([df_train_full[col].astype(str), df_active[col].astype(str), pd.Series(['Unknown'])])
    le.fit(combined_labels)
    encoders[col] = le
    
    df_train_full[col] = le.transform(df_train_full[col].astype(str))
    df_active[col] = le.transform(df_active[col].astype(str))

X = df_train_full[features]
y = df_train_full['IsWon_Target']

print("\n4. Training Machine Learning Model (Random Forest)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluation
y_pred = clf.predict(X_test)
y_prob = clf.predict_proba(X_test)[:, 1]
print("\nClassification Report (Test Set):")
print(classification_report(y_test, y_pred))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.3f}")

# Train on 100% of labeled data for final predictions
clf.fit(X, y)

# 6. Scoring Active Deals and Building Quarterly Revenue Forecast
print("\n5. Scoring Active Pipeline and Generating Risk-Adjusted Quarterly Forecast...")
X_active = df_active[features]
df_active['Win_Probability'] = clf.predict_proba(X_active)[:, 1]
df_active['Expected_Revenue'] = df_active['Un-Wtd Net Amount'] * df_active['Win_Probability']

# Map Expected Close Quarter using Expected FY and Expected FP
# Clean Expected FP to numeric
df_active['Expected_FP_Num'] = pd.to_numeric(df_active['Expected FP'], errors='coerce')

# Filter for the upcoming FY26 quarters (Q1/Q2/Q3/Q4)
# Let's see the fiscal quarters based on Expected FP (e.g. 202607 to 202609 is Q1, etc.)
# If Expected FP is in format YYYYMM, let's group by FP to generate the forecast
fp_forecast = df_active.groupby('Expected FP')[['Un-Wtd Net Amount', 'Expected_Revenue']].sum().reset_index()
print("\n--- RISK-ADJUSTED QUARTERLY FORECAST (BY FISCAL PERIOD) ---")
print(fp_forecast.to_string(index=False))

# Export Ranked Predictions
ranked_pipeline = df_active.sort_values(by='Expected_Revenue', ascending=False)
output_path = r"C:\Projects\GreyChain\ai\prediction-git\salesforce\quarterly_forecast_predictions.csv"
ranked_pipeline[['Opportunity Number', 'Client', 'Stage', 'Region', 'Business Unit', 'Un-Wtd Net Amount', 'Win_Probability', 'Expected_Revenue', 'Expected FP']].to_csv(output_path, index=False)
print(f"\nSuccessfully generated ranked active pipeline and saved quarterly forecast to:\n{output_path}")

# Print forecast summary
total_unweighted = df_active['Un-Wtd Net Amount'].sum()
total_risk_adjusted = df_active['Expected_Revenue'].sum()
print(f"\n--- FORECAST SUMMARY ---")
print(f"Total Unweighted Active Pipeline: ${total_unweighted:,.2f}")
print(f"Total Risk-Adjusted Active Pipeline (Forecast): ${total_risk_adjusted:,.2f}")
print(f"Overall Pipeline Win Rate (Value Weighted): {total_risk_adjusted / total_unweighted * 100:.1f}%")
