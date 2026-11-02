
import pandas as pd
import joblib

# Load trained model
model = joblib.load(
    "machine_learning/models/alertiq_model.joblib"
)

# Load sample records
data = pd.read_csv(
    "data/processed/alertiq_training.csv"
)

# Select 5 records for testing
X = data.drop(columns=["target"]).head(5)

# Predict attack probability
predictions = model.predict(X)
probabilities = model.predict_proba(X)[:, 1]

print("\n========== ALERTIQ AI PREDICTIONS ==========")

for i in range(len(X)):
    label = "ATTACK" if predictions[i] == 1 else "BENIGN"

    print(f"\nRecord {i + 1}")
    print("Prediction:", label)
    print("Attack Probability:", round(probabilities[i] * 100, 2), "%")

