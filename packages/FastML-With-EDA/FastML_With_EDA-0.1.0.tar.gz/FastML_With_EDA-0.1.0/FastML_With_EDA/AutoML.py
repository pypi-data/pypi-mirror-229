import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
import xgboost as xgb
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, confusion_matrix, precision_score, recall_score, f1_score
from .EDA_and_preprocessing import encode_categorical_features








def train_machine_learning_models(data, target_column, task_type, model_names=None, test_size = 0.2 , hyperparameters={}  , scaling=None):
    """
    Train machine learning models for regression or classification with optional feature scaling .

    Parameters:
    - data (pandas.DataFrame): The dataset containing features and target variable.
    - target_column (str): The name of the target variable column.
    - task_type (str): Either 'regression' or 'classification' for the type of task.
    - model_names (list, optional): List of model names to train. If None, train all available models[
        'linear',
        'logistic',
        'svm',
        'knn',
        'decision_tree',
        'random_forest',
        'boosting',
        'xgboost',
].
    - hyperparameters (dict, optional): Hyperparameters for the selected models. If None, default hyperparameters will be used.
    - scaling (str, optional): Type of feature scaling ('minmax' or 'standard').
    

    Returns:
    - Dictionary of trained models and their evaluation metrics.
    - DataFrame comparing the evaluation metrics of all models.
    - Best model based on the highest metric (R2-score for regression, F1-score for classification).

    Example usage:
    models , training_df ,testing_df ,best_model = train_machine_learning_models(data, 'target_column', 'classification', model_names=None, test_size = 0.2 ,hyperparameters={} ,scaling='minmax')
    """

    
    # Extract features (X) and target variable (y)
    X = data.drop(target_column, axis=1)
    y = data[target_column]


    object_columns = X.select_dtypes(include=['object'])

    if not object_columns.empty:
        X = encode_categorical_features(X ,type_of_encoding='onehot')
    else:
        pass

    

    # Apply feature scaling if specified
    if scaling == 'minmax':
        scaler = MinMaxScaler()
    elif scaling == 'standard':
        scaler = StandardScaler()
    else:
        scaler = None

    if scaler:
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = X

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, random_state=42)

    # Define available models
    available_models = {
        'linear': LinearRegression,
        'logistic': LogisticRegression,
        'svm': SVR if task_type == 'regression' else SVC,
        'knn': KNeighborsRegressor if task_type == 'regression' else KNeighborsClassifier,
        'decision_tree': DecisionTreeRegressor if task_type == 'regression' else DecisionTreeClassifier,
        'random_forest': RandomForestRegressor if task_type == 'regression' else RandomForestClassifier,
        'boosting': GradientBoostingRegressor if task_type == 'regression' else GradientBoostingClassifier,
        'xgboost': xgb.XGBRegressor if task_type == 'regression' else xgb.XGBClassifier,
    }

    # Initialize results
    models = {}
    training = []
    testing = []
    train_metrics = {}
    test_metrics = {}

    # Iterate through available models
    for model_name, model_class in available_models.items():
        if model_names is None:
            if task_type == 'regression':
                if model_name in ['logistic', 'svm', 'knn']:
                    continue  # Skip classification models for regression tasks
                model = model_class(**hyperparameters)
            elif task_type == 'classification':
                if model_name in ['linear', 'svm', 'knn']:
                    continue  # Skip regression models for classification tasks
                model = model_class(**hyperparameters)

            # Fit the model to the training data
            model.fit(X_train, y_train)

            # Evaluate the model on training and testing sets
            train_metrics = evaluate_model(model, X_train, y_train, task_type)
            test_metrics = evaluate_model(model, X_test, y_test, task_type)

            # Store the model and metrics
            models[model_name] = model
            # for k , v in train_metrics.items():
            if task_type == 'regression':
                training.append({
                    'Model': model_name,
                    'R2': train_metrics['R2-score'],
                    'MSE': train_metrics['MSE'],
                    'RMSE': train_metrics['RMSE'],
                    'MAE': train_metrics['MAE']
                })

                # for k , v in test_metrics.items():
                testing.append({
                    'Model': model_name,
                    'R2': test_metrics['R2-score'],
                    'MSE': test_metrics['MSE'],
                    'RMSE': test_metrics['RMSE'],
                    'MAE': test_metrics['MAE']
                })
            elif task_type == 'classification':
                training.append({
                    'Model': model_name,
                    'Precision': train_metrics['Precision'],
                    'Recall': train_metrics['Recall'],
                    'F1-score': train_metrics['F1-score'],
                    'Confusion Matrix': train_metrics['Confusion Matrix']
                })

                # for k , v in test_metrics.items():
                testing.append({
                    'Model': model_name,
                    'Precision': test_metrics['Precision'],
                    'Recall': test_metrics['Recall'],
                    'F1-score': test_metrics['F1-score'],
                    'Confusion Matrix': test_metrics['Confusion Matrix']
                })
            else:
                raise ValueError(
                    "Invalid task_type. Choose either 'regression' or 'classification'.")
            
        elif model_name in model_names:
            model = model_class(**hyperparameters)
            # Fit the model to the training data
            model.fit(X_train, y_train)
            # Evaluate the model on training and testing sets
            train_metrics = evaluate_model(model, X_train, y_train, task_type)
            test_metrics = evaluate_model(model, X_test, y_test, task_type)

    # Create a DataFrame comparing metrics of all models
    training_df = pd.DataFrame(training)
    testing_df = pd.DataFrame(testing)

    # Find the best model based on the highest metric
    # Find the best model based on the highest metric
    if model_names == None:
        if task_type == 'regression':
            best_model_name = testing_df.iloc[testing_df['R2'].idxmax(
            )]['Model']
        elif task_type == 'classification':
            best_model_name = testing_df.iloc[testing_df['F1-score'].idxmax()
                                              ]['Model']

        else:
            raise ValueError(
                "Invalid task_type. Choose either 'regression' or 'classification'.")

        best_model = models[best_model_name]

        return models, training_df, testing_df, best_model
    else:
        # train_metrics = evaluate_model(model, X_train, y_train, task_type)
        # test_metrics = evaluate_model(model, X_test, y_test, task_type)
        return models, train_metrics, test_metrics



# Helper function to evaluate the model
def evaluate_model(model, X, y, task_type):
    """
    Evaluate a machine learning model and calculate relevant metrics.

    Parameters:
    - model: Trained machine learning model.
    - X: Features.
    - y: True labels.
    - task_type (str): Either 'regression' or 'classification' for the type of task.

    Returns:
    - Dictionary of evaluation metrics.
    """
    metrics = {}
    if task_type == 'regression':
        y_pred = model.predict(X)
        metrics['R2-score'] = r2_score(y, y_pred)
        metrics['MSE'] = mean_squared_error(y, y_pred)
        metrics['RMSE'] = mean_squared_error(
            y, y_pred, squared=False)
        metrics['MAE'] = mean_absolute_error(y, y_pred)
    elif task_type == 'classification':
        y_pred = model.predict(X)
        metrics['Confusion Matrix'] = confusion_matrix(y, y_pred)
        metrics['Precision'] = precision_score(y, y_pred)
        metrics['Recall'] = recall_score(y, y_pred)
        metrics['F1-score'] = f1_score(y, y_pred)
    else:
        raise ValueError(
            "Invalid task_type. Choose either 'regression' or 'classification'.")

    return metrics
