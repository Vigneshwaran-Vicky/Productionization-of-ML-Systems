import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("Flight Price Prediction")

with mlflow.start_run():
    mlflow.log_param("test_param", 123)
    mlflow.log_metric("test_metric", 0.95)

print("DONE")
