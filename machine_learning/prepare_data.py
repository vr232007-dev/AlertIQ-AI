
import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

all_data = []

for file in RAW_DIR.glob("*.csv"):
    print(f"\nProcessing: {file.name}")

    df = pd.read_csv(file, low_memory=False)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Remove rows without labels
    df = df.dropna(subset=["Label"])

    # Clean labels
    df["Label"] = df["Label"].astype(str).str.strip()

    # Binary classification
    df["target"] = (df["Label"] != "BENIGN").astype("int8")

    # Sample up to 20,000 rows per file
    df = df.sample(
        n=min(20000, len(df)),
        random_state=42
    )

    # Remove original text label
    df = df.drop(columns=["Label"])

    # Convert features to numeric
    for col in df.columns:
        if col != "target":
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )

    # Handle infinite values
    df = df.replace([np.inf, -np.inf], np.nan)

    all_data.append(df)

# Combine all sampled data
combined = pd.concat(all_data, ignore_index=True)

# Remove duplicate records
combined = combined.drop_duplicates()

# Save prepared dataset
output_file = OUTPUT_DIR / "alertiq_training.csv"
combined.to_csv(output_file, index=False)

print("\n========== PREPARATION COMPLETE ==========")
print("Dataset shape:", combined.shape)
print("\nTarget distribution:")
print(combined["target"].value_counts())
print("\nSaved to:", output_file)
