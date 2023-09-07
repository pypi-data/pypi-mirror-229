# FastML_With_EDA

FastML_With_EDA is a versatile Python package designed to simplify the machine learning pipeline, from exploratory data analysis (EDA) and preprocessing to automated machine learning (AutoML) model training and evaluation. Whether you're a beginner or an experienced data scientist, FastML provides the tools you need to streamline your workflow and make data-driven decisions.

## Features

- **Data Loading:** Load data from various file formats, including CSV, Excel, and SQL databases.
- **Exploratory Data Analysis (EDA):** Explore your dataset with ease. Get insights into data types, summary statistics, unique values in categorical columns, and identify missing values.
- **Handling Missing Values:** Choose from different strategies to handle missing values, including mean and median imputation or removal of rows/columns.
- **Outlier Detection:** Detect and optionally remove outliers from numerical columns.
- **Data Visualization:** Generate various types of data visualizations, such as histograms, scatter plots, regression plots, and more, to gain a deeper understanding of your data.
- **Categorical Encoding:** Encode categorical features using Label Encoding or One-Hot Encoding.
- **AutoML:** Train machine learning models for both regression and classification tasks with optional feature scaling. FastML supports a variety of algorithms, including linear regression, logistic regression, SVM, k-nearest neighbors, decision trees, random forests, gradient boosting, and XGBoost.
- **Model Evaluation:** Evaluate trained models with common metrics such as R2-score, MSE, RMSE, MAE for regression, and Precision, Recall, F1-score, Confusion Matrix for classification.
- **Model Selection:** Automatically select the best-performing model based on your chosen evaluation metric.

## Installation

You can install FastML using pip:

```bash
pip install FastML
```

## Usage

Here's a basic example of how to use FastML for EDA and AutoML:

```python
import FastML

# Load your data
data = FastML.load_data('data.csv')

# Explore the data
FastML.explore_data(data)

# Handle missing values
data = FastML.handling_missing_values(data, missing_strategy='mean')

# Detect and remove outliers
data = FastML.outliers(data, remove=True)

# Visualize your data
FastML.plot_data(data, plot_type='histogram', x='feature_name')

# Encode categorical features
data_encoded = FastML.encode_categorical_features(data, type_of_encoding='onehot')

# Train machine learning models
models, training_df, testing_df, best_model = FastML.train_machine_learning_models(
    data, target_column='target', task_type='classification', model_names=None, test_size=0.2, hyperparameters={}, scaling='minmax'
)

# Evaluate models and select the best one
print(best_model)
```

For more detailed usage examples and documentation, please refer to the [FastML documentation](https://github.com/Veto2922/Fast-Machine-Learning-With-EDA/tree/main).

## Contributing

We welcome contributions from the open-source community. If you find any issues or have suggestions for improvements, please create a GitHub issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
