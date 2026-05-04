from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
import mysql.connector
from mysql.connector import Error
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Construction AI API with SQL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration (Priority: Environment Variables, Default: XAMPP)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "construction_db"),
    "port": int(os.getenv("DB_PORT", 3306))
}

def init_db():
    try:
        # Connect without database to create it if it doesn't exist
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"], 
            user=DB_CONFIG["user"], 
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prediction_type VARCHAR(50),
                predicted_value VARCHAR(255),
                interpretation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Error as e:
        print(f"Database error during initialization: {e}")

def save_prediction(pred_type, value, interpretation):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "INSERT INTO predictions (prediction_type, predicted_value, interpretation) VALUES (%s, %s, %s)"
        cursor.execute(query, (pred_type, str(value), interpretation))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error saving prediction to DB: {e}")

# Load models
MODELS_DIR = "models"
def load_model(name):
    path = os.path.join(MODELS_DIR, name)
    return joblib.load(path) if os.path.exists(path) else None

cost_model = load_model("cost_model.joblib")
cost_features = load_model("cost_features.joblib")
time_model = load_model("time_model.joblib")
time_features = load_model("time_features.joblib")
equip_model = load_model("equip_model.joblib")
equip_le = load_model("equip_label_encoder.joblib")
equip_features = load_model("equip_features.joblib")
seg_scaler = load_model("seg_scaler.joblib")
seg_pca = load_model("seg_pca.joblib")
seg_model = load_model("seg_model.joblib")
seg_features = load_model("seg_features.joblib")

init_db()

class ConstructionData(BaseModel):
    worker_count: float = 0.0
    machinery_status: float = 0.0
    task_progress: float = 0.0
    vibration_level: float = 0.0
    safety_incidents: float = 0.0
    material_shortage_alert: float = 0.0
    update_frequency: float = 0.0
    temperature: float = 0.0
    humidity: float = 0.0
    energy_consumption: float = 0.0
    risk_score: float = 0.0
    simulation_deviation: float = 0.0
    material_usage: float = 0.0
    equipment_utilization_rate: float = 0.0
    cost_deviation: float = 0.0
    time_deviation: float = 0.0

@app.get("/")
def read_root():
    return {"status": "online", "database": "connected (XAMPP)"}

@app.post("/predict/cost")
def predict_cost(data: ConstructionData):
    if not cost_model: raise HTTPException(status_code=500, detail="Model error")
    input_df = pd.DataFrame([data.dict()])
    prediction = float(cost_model.predict(input_df[cost_features])[0])
    interpretation = "Stable" if prediction < 5 else "Warning" if prediction < 15 else "Critical"
    save_prediction("Cost Deviation", f"{prediction:.2f}%", interpretation)
    return {"prediction": prediction, "interpretation": interpretation}

@app.post("/predict/time")
def predict_time(data: ConstructionData):
    if not time_model: raise HTTPException(status_code=500, detail="Model error")
    input_df = pd.DataFrame([data.dict()])
    prediction = float(time_model.predict(input_df[time_features])[0])
    interpretation = "On schedule" if prediction < 2 else "Watch" if prediction < 7 else "At risk"
    save_prediction("Time Delay", f"{prediction:.1f} Days", interpretation)
    return {"prediction": prediction, "interpretation": interpretation}

@app.post("/predict/equipment")
def predict_equipment(data: ConstructionData):
    if not equip_model: raise HTTPException(status_code=500, detail="Model error")
    input_df = pd.DataFrame([data.dict()])
    pred_idx = equip_model.predict(input_df[equip_features])[0]
    prediction = str(equip_le.inverse_transform([pred_idx])[0])
    mapping = {"Low": "Inefficient", "Medium": "Balanced", "High": "Intensive"}
    interpretation = mapping.get(prediction, "")
    save_prediction("Equipment Utilization", prediction, interpretation)
    return {"prediction": prediction, "interpretation": interpretation}

@app.post("/predict/segmentation")
def predict_segmentation(data: ConstructionData):
    if not seg_model: raise HTTPException(status_code=500, detail="Model error")
    input_df = pd.DataFrame([data.dict()])
    X_scaled = seg_scaler.transform(input_df[seg_features])
    X_pca = seg_pca.transform(X_scaled)
    cluster = int(seg_model.predict(X_pca)[0])
    cluster_info = {0: ("Standard", "Low risk"), 1: ("Complex", "High intensity"), 2: ("Optimized", "Efficient")}
    name, interpretation = cluster_info.get(cluster, (f"Cluster {cluster}", ""))
    save_prediction("Site Segmentation", name, interpretation)
    return {"cluster_id": cluster, "segment_name": name, "interpretation": interpretation}

@app.get("/history")
def get_history():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 50")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        return {"error": str(e)}

@app.get("/stats")
def get_stats():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM predictions")
        total = cursor.fetchone()["total"]
        
        cursor.execute("SELECT AVG(CAST(REPLACE(predicted_value, '%', '') AS DECIMAL(10,2))) as avg_cost FROM predictions WHERE prediction_type='Cost Deviation'")
        avg_cost = cursor.fetchone()["avg_cost"] or 0
        
        cursor.execute("SELECT COUNT(*) as alerts FROM predictions WHERE interpretation IN ('Critical', 'Warning', 'At risk')")
        alerts = cursor.fetchone()["alerts"]
        
        cursor.close()
        conn.close()
        return {"total": total, "avg_cost": round(float(avg_cost), 2), "alerts": alerts}
    except Error as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
