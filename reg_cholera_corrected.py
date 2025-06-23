
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
df = pd.read_csv("enriched_data_logical_cleaned.csv")

# Remove rows with non-numeric fatality rate
df = df[pd.to_numeric(df["Cholera case fatality rate"], errors='coerce').notnull()]
df["Cholera case fatality rate"] = df["Cholera case fatality rate"].astype(float)

# Bin Age into groups
df["Age_Group"] = pd.cut(
    df["Age"],
    bins=[0, 12, 18, 35, 50, 65, 100],
    labels=["Child", "Teen", "Young Adult", "Adult", "Middle Age", "Senior"]
)

# Create binary target: 1 if fatality rate > 1.0, else 0
df["Fatality_High"] = (df["Cholera case fatality rate"] > 1.0).astype(int)

# Select features and target
features = [
    "Sanitation_Level", "Access_to_Clean_Water", "Urban_or_Rural",
    "Vaccinated_Against_Cholera", "WHO Region", "Gender", "Age_Group"
]
X = df[features]
y = df["Fatality_High"]

# One-hot encode categorical features
X_encoded = pd.get_dummies(X)

# Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('log_reg', LogisticRegression(max_iter=1000))
])

# Fit the model
pipeline.fit(X_train, y_train)

# Evaluate the model
y_pred = pipeline.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(pipeline, "logreg_model.joblib")




joblib.dump(X_encoded.columns.tolist(), "cholera_model_columns.pkl")
