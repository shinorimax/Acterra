import pandas as pd
import json
from collections import defaultdict

# Define plan mappings for each CCA
cca_plan_map = {
    "San Jose Clean Energy": ["SJCE GreenSource", "SJCE Total Green"],
    "Silicon Valley Clean Energy": ["SVCE GreenStart", "SVCE GreenPrime"],
    "Ava Community Energy": ["Ava Bright Choice", "Ava Renewable 100"],
    "CleanPowerSF": ["CleanPowerSF SuperGreen", "CleanPowerSF Green (E-1)"],
    "Peninsula Clean Energy": ["SVCE GreenStart", "SVCE GreenPrime"],
    "MCE Clean Energy": ["MCE Light Green", "MCE Deep Green"],
    "Sonoma Clean Power": ["Sonoma Clean Power CleanStart", "Sonoma Clean Power EverGreen"],
}

# PG&E plans added to all ZIPs
pge_plans = ["PG&E Base Plan", "PG&E 50% Solar Choice"]

# Read your ZIP-CCA data into a DataFrame
# If your data is in a file, replace this with pd.read_csv or pd.read_table
# Example assumes a tab-delimited file with no header, and columns in order: ZIP, County, CCA
df = pd.read_csv("data/zip_code_data.csv")

# Drop duplicates to avoid double-counting plans
df = df.drop_duplicates()

zip_to_plans = {}

for i in range(len(df)):
    zip_code = str(df.iloc[i, 0])
    cca = df.iloc[i, 1]

    # Add CCA-specific plans first
    cca_plans = cca_plan_map.get(cca, [])
    plans = list(dict.fromkeys(cca_plans))  # preserves order, removes duplicates

    # Then add PG&E plans at the end (only if not already present)
    for pge_plan in pge_plans:
        if pge_plan not in plans:
            plans.append(pge_plan)

    # Add the ZIP code and its associated plans to the dictionary
    zip_to_plans[zip_code] = plans

# Write the result to a JSON file
with open("data/zip_to_energy_plans.json", "w") as f:
    json.dump(zip_to_plans, f, indent=2)

