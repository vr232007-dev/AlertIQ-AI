import pandas as pd
from pathlib import Path

data_folder = Path("data/raw")

for file in data_folder.glob("*.csv"):
    print("\n" + "=" * 60)
    print("FILE:", file.name)

    df = pd.read_csv(file, nrows=5, low_memory=False)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nSample data:")
    print(df.head(2))

    print("\nSample shape:", df.shape)