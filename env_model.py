import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import pickle

df = pd.read_csv("air_clean1.csv", engine="python", on_bad_lines="skip")

so2_col = "so2"
no2_col = "no2"

df = df.dropna(subset=[so2_col, no2_col])
df[so2_col] = pd.to_numeric(df[so2_col], errors="coerce")
df[no2_col] = pd.to_numeric(df[no2_col], errors="coerce")

so2_thresh = 40
no2_thresh = 50

df["damaged"] = ((df[so2_col] > so2_thresh) | (df[no2_col] > no2_thresh)).astype(int)

X = df[[so2_col, no2_col]]
y = df["damaged"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

with open("env_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved as env_model.pkl")
