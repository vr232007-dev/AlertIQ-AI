import pandas as pd
from pathlib import Path

data_folder = Path("data/raw")

all_labels = []

for file in data_folder.glob("*.csv"):
    print("\n" + "=" * 60)
    print("FILE:", file.name)

    df = pd.read_csv(file, low_memory=False)

    # Remove spaces from column names
    df.columns = df.columns.str.strip()

    # Clean label values
    df["Label"] = df["Label"].astype(str).str.strip()

    print("\nLabel distribution:")
    print(df["Label"].value_counts())

    all_labels.append(df["Label"])

print("\n" + "=" * 60)
print("COMBINED LABEL DISTRIBUTION")

combined = pd.concat(all_labels, ignore_index=True)
print(combined.value_counts())