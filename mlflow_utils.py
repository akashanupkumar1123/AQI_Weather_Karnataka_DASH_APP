import os
import pandas as pd
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

# Default path to the MLflow summary CSV file
MLFLOW_SUMMARY_PATH = os.path.abspath(os.path.join("mlruns", "mlflow_summary.csv"))

def load_mlflow_summary(path=MLFLOW_SUMMARY_PATH):
    """
    Load the MLflow experiment summary from CSV.
    Returns:
        pd.DataFrame: Summary data, or empty DataFrame if error/missing file.
    """
    if not os.path.exists(path):
        logger.warning(f"⚠️ File not found: {path}")
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as e:
        logger.error(f"❌ Error reading {path}: {e}")
        return pd.DataFrame()


def list_experiments():
    """
    Return a sorted list of unique experiment names from the summary CSV.
    Only non-null experiment names are included.
    """
    df = load_mlflow_summary()
    return sorted(df["Experiment"].dropna().unique()) if not df.empty else []


def get_latest_mlflow_stats(experiment_name=None):
    """
    Get the latest run stats for an experiment from the summary CSV.

    Args:
        experiment_name (str, optional): If provided, filters to this experiment.
                                         If None, uses the most recent run overall.

    Returns:
        tuple: (experiment_name, run_id, metrics_dict, params_dict)
               metrics_dict includes RMSE and MSE.
               params_dict includes custom parameters like Metric Type.
    """
    df = load_mlflow_summary()
    if df.empty:
        return "No Data", "N/A", {}, {}

    # Filter by experiment name if provided
    if experiment_name:
        df = df[df["Experiment"] == experiment_name]

    if df.empty:
        return experiment_name or "Unknown", "Not Found", {}, {}

    # Select the most recent entry (assumes CSV ordered by recency)
    latest = df.iloc[0]

    experiment_name = latest.get("Experiment", "Unknown")
    run_id = latest.get("Run ID", "N/A")

    metrics = {
        "RMSE": float(latest.get("RMSE", 0.0)),
        "MSE": float(latest.get("MSE", 0.0))
    }
    params = {
        "Metric Type": latest.get("Metric", "N/A")
    }
    return experiment_name, run_id, metrics, params
