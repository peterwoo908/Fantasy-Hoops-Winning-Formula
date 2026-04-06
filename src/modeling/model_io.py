import joblib

from src.config import FP_MODEL_PATH, MIN_MODEL_PATH


def load_model(path):
    return joblib.load(path)


def load_production_models(min_model_path=MIN_MODEL_PATH, fp_model_path=FP_MODEL_PATH):
    return load_model(min_model_path), load_model(fp_model_path)
