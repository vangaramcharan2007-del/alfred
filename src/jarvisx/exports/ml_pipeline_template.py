"""
Genesis Omega ML Pipeline Template
Demonstrates a core Machine Learning pipeline using scikit-learn.
"""

# 1. Imports
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

def execute_ml_pipeline():
    # 2. Data Loading
    print("Loading Iris dataset...")
    data = load_iris()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = data.target

    # 3. Data Preprocessing: Splitting into training and testing sets
    # We use 20% of the data for testing and 80% for training.
    print("Splitting data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Data Preprocessing: Scaling features
    # Standardization transforms the data such that it has a mean of 0 and a standard deviation of 1.
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 5. Model Initialization and Training
    # We initialize a Random Forest Classifier with 100 trees.
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    # 6. Evaluation
    # We predict the labels for the test set and evaluate the accuracy.
    print("Evaluating model...")
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=data.target_names))

if __name__ == "__main__":
    execute_ml_pipeline()
