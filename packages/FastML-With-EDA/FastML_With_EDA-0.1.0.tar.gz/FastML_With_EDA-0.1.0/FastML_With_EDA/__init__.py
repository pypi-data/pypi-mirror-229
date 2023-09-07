
"""
FastML Machine Learning Toolkit Module

This package provides a set of functions and tools for machine learning tasks, including data preprocessing, model training, and evaluation. It includes functions for loading data, exploring dataset statistics, handling missing values, detecting outliers, training machine learning models for regression or classification, and evaluating model performance.

Functions:
- load_data(data_source): Load data from various file formats.
- explore_data(data): Explore basic dataset information and statistics.
- handling_missing_values(data, missing_strategy='mean'): Handle missing values in the dataset.
- outliers(data, precentage=True, remove=False): Detect and optionally remove outliers in numerical columns.
- plot_data(data, plot_type, x=None, y=None): Generate various types of data visualization plots.
- encode_categorical_features(data, type_of_encoding): Encode categorical features using Label Encoding or One-Hot Encoding.
- train_machine_learning_models(data, target_column, task_type, model_names=None, test_size=0.2, hyperparameters={}, scaling=None): Train machine learning models with optional feature scaling and hyperparameter tuning.
- evaluate_model(model, X, y, task_type): Evaluate a machine learning model and calculate relevant metrics.

Dependencies:
- pandas
- numpy
- argparse
- matplotlib.pyplot
- seaborn
- sklearn.preprocessing.OneHotEncoder
- sklearn.model_selection.train_test_split
- sklearn.linear_model.LinearRegression, LogisticRegression
- sklearn.svm.SVC, SVR
- sklearn.neighbors.KNeighborsClassifier, KNeighborsRegressor
- sklearn.tree.DecisionTreeClassifier, DecisionTreeRegressor
- sklearn.ensemble.RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
- xgboost
- sklearn.preprocessing.StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
- sklearn.compose.ColumnTransformer
- sklearn.pipeline.Pipeline
- sklearn.metrics.mean_squared_error, mean_absolute_error, r2_score, confusion_matrix, precision_score, recall_score, f1_score
- .preprocessing.encode_categorical_features

Example usage:
models, training_df, testing_df, best_model = train_machine_learning_models(data, 'target_column', 'classification', model_names=None, test_size=0.2, hyperparameters={}, scaling='minmax')
"""

# Import statements for your functions and dependencies go here
