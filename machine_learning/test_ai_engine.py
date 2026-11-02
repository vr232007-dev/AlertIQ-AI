
import pandas as pd
from ai_engine import predict_alert

# Load one sample record
data = pd.read_csv("data/processed/alertiq_training.csv")

# Get features without the target column
sample = data.drop(columns=["target"]).iloc[0].to_dict()

# Call AI engine
result = predict_alert(sample)

print("\n========== ALERTIQ AI ENGINE TEST ==========")
print(result)
