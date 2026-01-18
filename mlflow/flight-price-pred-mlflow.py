import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import logging
import os
os.environ["MLFLOW_ENABLE_EMOJI"] = "false"

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

mlflow.set_tracking_uri("http://127.0.0.1:5000")
logging.getLogger('mlflow').handlers = []
mlflow.set_experiment("Flight Price Prediction1")

# =========================
# Start MLflow run
# =========================
with mlflow.start_run():

    print("Loading data...")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "flights.csv")
    df = pd.read_csv(csv_path)

    # =========================
    # Feature Engineering
    # =========================
    df["date"] = pd.to_datetime(df["date"])

    df["week_day"] = df["date"].dt.weekday
    df["week_no"] = df["date"].dt.isocalendar().week.astype(int)
    df["day"] = df["date"].dt.day

    df.rename(columns={"to": "destination"}, inplace=True)

    df["flight_speed"] = df["distance"] / df["time"]

    df = pd.get_dummies(df, columns=["from", "destination", "flightType", "agency"])

    df.drop(columns=["time", "flight_speed", "distance", "month", "year"], errors="ignore", inplace=True)

    # =========================
    # Split features & target
    # =========================
    X = df.drop("price", axis=1)
    y = df["price"]

    X.rename(
        columns={
            "from_Sao Paulo (SP)": "from_Sao_Paulo (SP)",
            "from_Rio de Janeiro (RJ)": "from_Rio_de_Janeiro (RJ)",
            "from_Campo Grande (MS)": "from_Campo_Grande (MS)",
            "destination_Sao Paulo (SP)": "destination_Sao_Paulo (SP)",
            "destination_Rio de Janeiro (RJ)": "destination_Rio_de_Janeiro (RJ)",
            "destination_Campo Grande (MS)": "destination_Campo_Grande (MS)",
        },
        inplace=True,
    )

    features_ordering = [
        "from_Florianopolis (SC)", "from_Sao_Paulo (SP)", "from_Salvador (BH)",
        "from_Brasilia (DF)", "from_Rio_de_Janeiro (RJ)", "from_Campo_Grande (MS)",
        "from_Aracaju (SE)", "from_Natal (RN)", "from_Recife (PE)",
        "destination_Florianopolis (SC)", "destination_Sao_Paulo (SP)",
        "destination_Salvador (BH)", "destination_Brasilia (DF)",
        "destination_Rio_de_Janeiro (RJ)", "destination_Campo_Grande (MS)",
        "destination_Aracaju (SE)", "destination_Natal (RN)", "destination_Recife (PE)",
        "flightType_economic", "flightType_firstClass", "flightType_premium",
        "agency_Rainbow", "agency_CloudFy", "agency_FlyingDrops",
        "week_no", "week_day", "day"
    ]

    X = X[features_ordering]

    # =========================
    # Train / Test split
    # =========================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # =========================
    # Scaling (optional for RF, kept for consistency)
    # =========================
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # =========================
    # Model + GridSearch (CORRECT)
    # =========================
    print("Starting GridSearchCV...")

    rf_model = RandomForestRegressor(
        random_state=42,
        n_jobs=-1
    )

    param_grid = {
        "n_estimators": [300],
        "max_depth": [15],
        "min_samples_split": [10],
        "max_features": ["sqrt", 27]
    }

    rf_grid = GridSearchCV(
        estimator=rf_model,
        param_grid=param_grid,
        cv=3,
        scoring="r2",
        verbose=2
    )

    rf_grid.fit(X_train, y_train)

    best_model = rf_grid.best_estimator_

    print("GridSearch completed")

    # =========================
    # Predictions & Metrics
    # =========================
    y_pred = best_model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    # =========================
    # MLflow logging
    # =========================
    mlflow.log_params(rf_grid.best_params_)
    mlflow.log_param("test_size", 0.2)
    mlflow.log_param("random_state", 42)

    mlflow.log_metric("MAE", mae)
    mlflow.log_metric("MSE", mse)
    mlflow.log_metric("RMSE", rmse)
    mlflow.log_metric("R2", r2)

    mlflow.sklearn.log_model(best_model, "random_forest_model")

    print("Run completed successfully")
