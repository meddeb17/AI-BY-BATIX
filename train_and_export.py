import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import os

# Create directory for models
os.makedirs('backend/models', exist_ok=True)

def train_models():
    print("Loading dataset...")
    df = pd.read_csv('construction_project_dataset_updated.csv')

    # Preprocessing
    # Median imputation for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    # 1. Cost Deviation Model
    print("Training Cost Deviation Model...")
    cost_features = [
        'worker_count', 'machinery_status', 'task_progress',
        'vibration_level', 'safety_incidents',
        'material_shortage_alert', 'update_frequency'
    ]
    X_cost = df[cost_features]
    y_cost = df['cost_deviation']
    
    cost_model = RandomForestRegressor(n_estimators=100, random_state=42)
    cost_model.fit(X_cost, y_cost)
    joblib.dump(cost_model, 'backend/models/cost_model.joblib')
    joblib.dump(cost_features, 'backend/models/cost_features.joblib')

    # 2. Time Deviation Model (Delay)
    print("Training Time Deviation Model...")
    time_features = [
        'worker_count', 'machinery_status', 'task_progress',
        'vibration_level', 'temperature', 'humidity'
    ]
    X_time = df[time_features]
    y_time = df['time_deviation']
    
    time_model = RandomForestRegressor(n_estimators=100, random_state=42)
    time_model.fit(X_time, y_time)
    joblib.dump(time_model, 'backend/models/time_model.joblib')
    joblib.dump(time_features, 'backend/models/time_features.joblib')

    # 3. Chantier Segmentation (PCA + KMeans)
    print("Training Segmentation Model...")
    # Features used in notebook for segmentation
    seg_features = [
        'temperature', 'humidity', 'vibration_level', 'material_usage',
        'worker_count', 'energy_consumption', 'task_progress',
        'cost_deviation', 'time_deviation', 'safety_incidents',
        'equipment_utilization_rate', 'risk_score'
    ]
    X_seg = df[seg_features]
    
    # Scaling for PCA/KMeans
    scaler = StandardScaler()
    X_seg_scaled = scaler.fit_transform(X_seg)
    
    # PCA
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_seg_scaled)
    
    # KMeans (k=3 as a reasonable default from notebook analysis)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X_pca)
    
    joblib.dump(scaler, 'backend/models/seg_scaler.joblib')
    joblib.dump(pca, 'backend/models/seg_pca.joblib')
    joblib.dump(kmeans, 'backend/models/seg_model.joblib')
    joblib.dump(seg_features, 'backend/models/seg_features.joblib')

    # 4. Equipment Utilization Classification
    print("Training Equipment Utilization Model...")
    df['utilization_class'] = pd.cut(
        df['equipment_utilization_rate'],
        bins=[df['equipment_utilization_rate'].min(), 60, 75, df['equipment_utilization_rate'].max()],
        labels=['Low', 'Medium', 'High'],
        include_lowest=True
    )
    
    equip_features = [
        'worker_count', 'machinery_status', 'task_progress',
        'vibration_level', 'temperature', 'humidity', 'energy_consumption', 'risk_score'
    ]
    
    X_equip = df[equip_features]
    y_equip = df['utilization_class'].astype(str)
    
    le = LabelEncoder()
    y_equip_enc = le.fit_transform(y_equip)
    
    equip_model = RandomForestClassifier(n_estimators=100, random_state=42)
    equip_model.fit(X_equip, y_equip_enc)
    
    joblib.dump(equip_model, 'backend/models/equip_model.joblib')
    joblib.dump(le, 'backend/models/equip_label_encoder.joblib')
    joblib.dump(equip_features, 'backend/models/equip_features.joblib')

    print("All models (Cost, Time, Segmentation, Equipment) trained and exported.")

if __name__ == "__main__":
    train_models()
