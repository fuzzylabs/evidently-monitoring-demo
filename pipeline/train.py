"""Model training."""
import logging
import os
import pickle
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from setup_logger import setup_logger


def prepare_data(
    data_path: str, features: list, target: str, test_size: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load, selected features and split dataset into train and test.

    Args:
        data_path (str): the path of the reference dataset
        features (list): features to be used
        target (str): the name of the target
        test_size (float): the test_size for train test split

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: the x and y for train and test split
    """
    if not os.path.exists(data_path):
        logging.error(f"Reference data does not exists in path: {data_path}")
        exit("Failed to load data")

    logging.info("Preparing data for train and test")
    df = pd.read_csv(data_path, index_col="date")

    x = df[features].values
    y = df[target].values

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=28
    )

    return x_train, x_test, y_train, y_test


def model_setup() -> RandomForestRegressor:
    """Initalise and return the regression model.

    Returns:
        RandomForestRegressor: a random forest regressor

    """
    logging.info("Creating Random Forest Regressor model")
    model = RandomForestRegressor(random_state=28, verbose=1)
    return model


def train(
    model: RandomForestRegressor, x_train: np.ndarray, y_train: np.ndarray
) -> None:
    """Fit the model using the train set.

    Args:
        model (RandomForestRegressor): the model to be trained
        x_train (np.ndarray): the training dataset
        y_train (np.ndarray): the ground truth of the training dataset
    """
    logging.info("Training model")
    model.fit(x_train, y_train)
    logging.info("Training Completed")


def evaluate(
    model: RandomForestRegressor, x_test: np.ndarray, y_test: np.ndarray
) -> None:
    """Evaluate the model and show the metrics.

    Args:
        model (RandomForestRegressor): the trained model to be evaluated
        x_test (np.ndarray): the testing dataset
        y_test (np.ndarray): the ground truth of the testing dataset
    """
    logging.info("Evaluating model on test set")
    predictions = model.predict(x_test)
    mse = mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions, squared=False)
    r2 = r2_score(y_test, predictions)

    logging.info(f"Mean Squared Error: {mse}")
    logging.info(f"Mean Absolute Error: {mae}")
    logging.info(f"Root Mean Squared Error: {rmse}")
    logging.info(f"R-Squared: {r2}")


def save_model(model: RandomForestRegressor) -> None:
    """Save the trained model using pickle into the models folder.

    Args:
        model (RandomForestRegressor): the trained model to be saved
    """
    with open("models/model.pkl", "wb") as f:
        pickle.dump(model, f)


if __name__ == "__main__":
    setup_logger()

    data_path = "datasets/house_price_random_forest/reference.csv"
    features = [
        "bedrooms",
        "bathrooms",
        "sqft_living",
        "sqft_lot",
        "floors",
        "waterfront",
        "view",
        "condition",
        "grade",
        "yr_built",
    ]
    target = "price"
    test_size = 0.2

    x_train, x_test, y_train, y_test = prepare_data(
        data_path, features, target, test_size
    )

    model = model_setup()
    train(model, x_train, y_train)
    evaluate(model, x_test, y_test)
    save_model(model)
