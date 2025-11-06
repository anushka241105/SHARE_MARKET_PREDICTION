import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os

def load_and_forecast(n_days=5, graph_type="line"):
    """
    Forecast stock prices using an LSTM model and return graph as Base64 string.
    graph_type options: 'line', 'bar', 'scatter', 'pie'
    """

    data_path = r"C:/Infosys_smp/SHARE_MARKET_PREDICTION/dataset.csv"
    model_path = r"C:/Infosys_smp/SHARE_MARKET_PREDICTION/models/lstm_close_model.h5"
    scaler_path = r"C:/Infosys_smp/SHARE_MARKET_PREDICTION/models/lstm_scaler.pkl"

    # ------------------------- Load Data -------------------------
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at: {data_path}")

    df = pd.read_csv(data_path)
    df.columns = df.columns.str.strip().str.capitalize()

    if 'Close' not in df.columns:
        raise ValueError("Dataset must contain a 'Close' column.")

    df = df[['Close']].dropna()
    close_prices = df.values

    # ------------------------- Load Model + Scaler -------------------------
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError("Model or scaler file missing.")

    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    # ------------------------- Prepare Data -------------------------
    scaled_data = scaler.transform(close_prices)
    last_60_days = scaled_data[-60:]
    X_input = np.array([last_60_days])

    # ------------------------- Predict Future -------------------------
    predictions = []
    for _ in range(n_days):
        pred = model.predict(X_input, verbose=0)
        predictions.append(pred[0])
        X_input = np.append(X_input[:, 1:, :], [[pred]], axis=1)

    predictions = scaler.inverse_transform(predictions)

    # ------------------------- Generate Dates -------------------------
    last_date = pd.Timestamp.today()
    future_dates = pd.date_range(start=last_date, periods=n_days, freq='D')

    # ------------------------- Plot Based on User Choice -------------------------
    plt.figure(figsize=(10, 5))

    if graph_type == "line":
        plt.plot(df['Close'].values[-100:], label="Actual", color="#00adb5", linewidth=2)
        plt.plot(range(len(df), len(df) + n_days), predictions, '--', label="Forecast", color="#ff6f61", linewidth=2)

    elif graph_type == "bar":
        plt.bar(future_dates, predictions.flatten(), color="#ff6f61", alpha=0.8)
        plt.plot(df['Close'].values[-20:], label="Recent Trend", color="#00adb5", linewidth=2)

    elif graph_type == "scatter":
        plt.scatter(future_dates, predictions.flatten(), color="#ff6f61", s=80, label="Predicted Points")

    elif graph_type == "pie":
        plt.pie(predictions.flatten(), labels=[f"Day {i+1}" for i in range(n_days)],
                autopct='%1.1f%%', startangle=90, colors=plt.cm.coolwarm(np.linspace(0, 1, n_days)))

    else:
        raise ValueError("Invalid graph_type. Choose from: line, bar, scatter, pie")

    plt.title(f"Stock Forecast ({graph_type.capitalize()} Chart)")
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)

    # ------------------------- Convert to Base64 -------------------------
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    encoded_graph = base64.b64encode(buf.getvalue()).decode("utf-8")

    return encoded_graph
