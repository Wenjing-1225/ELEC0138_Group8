import kagglehub
import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
from pathlib import Path

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")

# Download the dataset
path = kagglehub.dataset_download("isatish/phishing-dataset-uci-ml-csv")
print("The dataset has been downloaded to：", path)

# Find the CSV file
csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
print("CSV file has been found：", csv_files)

# Load dataset
df = pd.read_csv(os.path.join(path, "uci-ml-phishing-dataset.csv"))

# Save the dataset to the current directory
output_path = os.path.join("Attack", "phishing", "model", "uci-ml-phishing-dataset.csv")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)
print("The dataset has been saved as:", output_path)

# Features and Labels
X = df.drop("Result", axis=1)
y = df["Result"]

# Save feature column names to a file for inference use
feature_columns_path = os.path.join(ROOT_DIR, "feature_columns.txt")
with open(feature_columns_path, "w") as f:
    for col in X.columns:
        f.write(col + "\n")
print(f"Feature column names saved to: {feature_columns_path}")

# Data partitioning
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save the model
model_path = os.path.join(ROOT_DIR, "phishing_model.pkl")
joblib.dump(model, model_path)
print("The model has been saved as:", model_path)
