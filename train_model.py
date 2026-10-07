import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

def generate_dataset(filepath="dataset.csv", num_samples=2500, seed=42):
    """
    Generates a realistic loan approval dataset based on standard banking credit risk rules
    and saves it to dataset.csv.
    """
    np.random.seed(seed)
    
    ages = np.random.randint(21, 68, size=num_samples)
    incomes = np.random.exponential(scale=40000, size=num_samples) + 20000
    incomes = np.clip(incomes, 18000, 250000).astype(int)
    
    # Credit score following a normal distribution between 300 and 850
    credit_scores = np.random.normal(loc=675, scale=80, size=num_samples)
    credit_scores = np.clip(credit_scores, 300, 850).astype(int)
    
    # Loan amount scaled relative to income
    loan_amounts = incomes * np.random.uniform(0.4, 4.0, size=num_samples)
    loan_amounts = np.clip(loan_amounts, 3000, 150000).astype(int)
    
    loan_terms = np.random.choice([12, 24, 36, 48, 60, 120, 180, 360], size=num_samples, p=[0.1, 0.15, 0.3, 0.15, 0.15, 0.05, 0.05, 0.05])
    employment_statuses = np.random.choice(['Employed', 'Self-Employed', 'Unemployed', 'Retired'], size=num_samples, p=[0.65, 0.20, 0.08, 0.07])
    existing_loans = np.random.choice([0, 1, 2, 3, 4], size=num_samples, p=[0.4, 0.35, 0.15, 0.07, 0.03])
    education_levels = np.random.choice(['Graduate', 'Not Graduate'], size=num_samples, p=[0.75, 0.25])
    self_employed = np.where(employment_statuses == 'Self-Employed', 'Yes', 'No')
    dependents = np.random.choice([0, 1, 2, 3, 4], size=num_samples, p=[0.45, 0.25, 0.18, 0.08, 0.04])
    
    # Financial assessment score
    dti_ratio = loan_amounts / (incomes + 1e-5)
    
    score = np.zeros(num_samples)
    
    # Credit score contribution
    score += ((credit_scores - 300) / 550.0) * 45.0
    
    # DTI ratio contribution (lower DTI is better)
    score += np.clip((3.5 - dti_ratio) / 3.0 * 35.0, -10, 35)
    
    # Employment contribution
    emp_bonus = np.where(employment_statuses == 'Employed', 12,
                np.where(employment_statuses == 'Self-Employed', 7,
                np.where(employment_statuses == 'Retired', 5, -20)))
    score += emp_bonus
    
    # Education bonus
    score += np.where(education_levels == 'Graduate', 5, 0)
    
    # Existing loans & dependents impact
    score -= existing_loans * 3.5
    score -= dependents * 2.0
    
    # Slight realistic noise
    noise = np.random.normal(0, 4.0, size=num_samples)
    final_score = score + noise
    
    # Loan Status: Approved (1) if final score >= 45, else Rejected (0)
    loan_status = (final_score >= 45).astype(int)
    
    df = pd.DataFrame({
        'Age': ages,
        'AnnualIncome': incomes,
        'CreditScore': credit_scores,
        'LoanAmount': loan_amounts,
        'LoanTerm': loan_terms,
        'EmploymentStatus': employment_statuses,
        'ExistingLoans': existing_loans,
        'Education': education_levels,
        'SelfEmployed': self_employed,
        'Dependents': dependents,
        'LoanStatus': loan_status
    })
    
    df.to_csv(filepath, index=False)
    print(f"[+] Dataset successfully generated and saved to '{filepath}' with {num_samples} records.")
    return df

def train_and_evaluate():
    dataset_path = "dataset.csv"
    if not os.path.exists(dataset_path):
        print("Dataset not found. Generating new realistic loan approval dataset...")
        df = generate_dataset(dataset_path)
    else:
        print(f"Loading dataset from '{dataset_path}'...")
        df = pd.read_csv(dataset_path)

    print(f"Dataset shape: {df.shape}")
    
    # Handle missing values if any
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].median())
            
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].mode()[0])
            
    # Define features and target
    X = df.drop(columns=['LoanStatus'])
    y = df['LoanStatus']

    numeric_features = ['Age', 'AnnualIncome', 'CreditScore', 'LoanAmount', 'LoanTerm', 'ExistingLoans', 'Dependents']
    categorical_features = ['EmploymentStatus', 'Education', 'SelfEmployed']

    # Preprocessing Pipeline
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    # Full Model Pipeline using Random Forest Classifier
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=150, max_depth=15, min_samples_split=2, random_state=42))
    ])

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    print("Training Random Forest Classifier model...")
    pipeline.fit(X_train, y_train)

    # Evaluate model
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print("\n" + "="*50)
    print("      MODEL EVALUATION METRICS (TEST SET)      ")
    print("="*50)
    print(f"Accuracy : {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall   : {rec * 100:.2f}%")
    print(f"F1 Score : {f1 * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("="*50 + "\n")

    # Package model metadata
    model_data = {
        'pipeline': pipeline,
        'numeric_features': numeric_features,
        'categorical_features': categorical_features,
        'metrics': {
            'accuracy': round(acc * 100, 2),
            'precision': round(prec * 100, 2),
            'recall': round(rec * 100, 2),
            'f1_score': round(f1 * 100, 2),
            'confusion_matrix': cm.tolist()
        }
    }

    model_path = "model.pkl"
    joblib.dump(model_data, model_path)
    print(f"[+] Model and preprocessing pipeline successfully saved to '{model_path}'")

if __name__ == "__main__":
    train_and_evaluate()
