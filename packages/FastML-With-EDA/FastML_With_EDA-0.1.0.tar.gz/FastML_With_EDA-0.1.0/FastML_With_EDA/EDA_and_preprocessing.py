import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
import pandas as pd



def load_data(data_source):
        """
    Load data from various file formats (.csv, .xlsx, .xls, .sql).

    Parameters:
    -----------
    data_source : str
        Path to the data source file.

    Returns:
    --------
    pandas.DataFrame
        Loaded data as a DataFrame.
    
    Raises:
    -------
    ValueError
        If the data source format is not supported.
    """
        

        try:
            if data_source.endswith('.csv'):
                df = pd.read_csv(data_source)
            elif data_source.endswith('.xlsx') or data_source.endswith('.xls'):
                df = pd.read_excel(data_source)
            elif data_source.endswith('.sql'):
                df = pd.read_sql(data_source)
            else:
                raise ValueError("Unsupported data source")
            return df
        except:
             raise ValueError('Please add r before data source EX:  r\'data.csv\' ')




def explore_data(data):
        """
    Explore basic information and statistics of the dataset.

    Parameters:
    -----------
    data : pandas.DataFrame
        Input data to explore.

    Returns:
    --------
    None
    """
        print("Basic Information:")
        print("Number of rows:", data.shape[0])
        print("Number of columns:", data.shape[1])
        print('*' * 50)

        print("\nData Types:")
        print(data.dtypes)
        print('*' * 50)

        numerical_columns = data.select_dtypes(include=['int64', 'float64'])
        if not numerical_columns.empty:
            print("\nSummary Statistics for Numerical Columns:")
            print(numerical_columns.describe())
            print('*' * 50)
        else:
            print("\nNo numerical columns found.")
            print('*' * 50)

        categorical_columns = data.select_dtypes(include=['object'])
        if not categorical_columns.empty:
            print("\nUnique Values in Categorical Columns:")
            for column in categorical_columns.columns:
                unique_values = data[column].nunique()
                print(f"{column}: {unique_values} unique values")
                print('*' * 50)
        else:
            print("\nNo categorical columns found.")
            print('*' * 50)

        null_counts = data.isnull().sum()
        total_cells = data.shape[0]
        print("\nMissing Values:")
        for column, null_count in null_counts.items():
            if null_count > 0:
                percentage = (null_count / total_cells) * 100
                print(f"{column}: {null_count} missing ({percentage:.2f}%)")
                print('*' * 50)



def handling_missing_values(data, missing_strategy='mean'):
        """
    Handle missing values in the dataset.

    Parameters:
    -----------
    data : pandas.DataFrame
        Input data with missing values.
    missing_strategy : str, optional
        Strategy for handling missing values ('mean', 'median', 'remove').

    Returns:
    --------
    pandas.DataFrame
        Data with missing values handled.

    """
        print('*' * 100)
        print('Go to handling missing values -------------------')
        print(data.isna().sum() / len(data) * 100)
        print('*' * 100)

        for column in data.columns:
            pre = data[column].isna().sum() / len(data) * 100
            if pre <= 3:
                data = data.dropna(subset=[column])
                print(f'Droping rows for {column} < than 3% missing ----')

            elif 3 < pre < 90:
                if data[column].dtype == "object":
                    if missing_strategy == "remove":
                        data = data.dropna(subset=[column])
                    elif missing_strategy in ["mean", "median"]:
                        data[column] = data[column].fillna(
                            data[column].mode()[0])
                elif data[column].dtype in ["int64", "float64"]:
                    if missing_strategy == "remove":
                        data = data.dropna(subset=[column])
                    elif missing_strategy == "mean":
                        data[column] = data[column].fillna(
                            data[column].mean())
                    elif missing_strategy == "median":
                        data[column] = data[column].fillna(
                            data[column].median())
                # print(f'fill {missing_strategy} for rows for {column} > 3% missing and < 90%  ----' )

            else:
                data = data.drop(column, axis=1)
                print(f'Droping column = {column} >  90% missing ----')

        return data


def outliers(data, precentage=True, remove=False):
    """
    Detect and optionally remove outliers in numerical columns.

    Parameters:
    -----------
    data : pandas.DataFrame
        Input data.
    precentage : bool, optional
        If True, calculate and print outlier percentages.
    remove : bool, optional
        If True, remove outliers from the dataset.

    Returns:
    --------
    pandas.DataFrame or None
        Data with outliers removed if 'remove' is True, else None.
    
    """
    if precentage:
        outlier_percentages = {}

        for col in data.select_dtypes(include=["int64", "float64"]):
            q1 = data[col].quantile(0.25)
            q3 = data[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)]
            outlier_percentage = (len(outliers) / len(data)) * 100
            outlier_percentages[col] = outlier_percentage

        for key, value in outlier_percentages.items():
            print(f"\nThe outliers percentage in {key} = {value}")
            print("*" * 50)

    else:
        pass

    if remove:
        for col in data.select_dtypes(include=["int64", "float64"]):
            q1 = data[col].quantile(0.25)
            q3 = data[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            data = data[(data[col] >= lower_bound) & (data[col] <= upper_bound)]
        print('Removing outliers is done :)')
        return data
    


def plot_data(data, plot_type, x=None, y=None):
    """
    Generate various types of data visualization plots.

    Parameters:
    -----------
    data : pandas.DataFrame
        Input data.
    plot_type : str
        Type of plot ('histogram', 'kde', 'ecdf', 'regression', 'pairplot', 'scatter',
        'line', 'box', 'count', 'bar', 'point').
    x : str, optional
        X-axis data column name.
    y : str, optional
        Y-axis data column name (required for some plot types).

    Returns:
    --------
    None
    """
    if plot_type == 'histogram':
        sns.histplot(data[x], kde=True)
        plt.title(f'Histogram of {x}')
        plt.xlabel(x)
        plt.ylabel('Frequency')
    elif plot_type == 'kde':
        sns.kdeplot(data[x], shade=True)
        plt.title(f'KDE Plot of {x}')
        plt.xlabel(x)
        plt.ylabel('Density')
    elif plot_type == 'ecdf':
        sns.ecdfplot(data=data, x=x)
        plt.title(f'ECDF Plot of {x}')
        plt.xlabel(x)
        plt.ylabel('Cumulative Probability')
    elif plot_type == 'regression':
        sns.regplot(data=data, x=x, y=y)
        plt.title(f'Regression Plot of {x} vs {y}')
        plt.xlabel(x)
        plt.ylabel(y)
    elif plot_type == 'pairplot':
        sns.pairplot(data)
        plt.suptitle('Pair Plot of Numerical Columns')
    elif plot_type == 'scatter':
        sns.scatterplot(data=data, x=x, y=y)
        plt.title(f'Scatter Plot of {x} vs {y}')
        plt.xlabel(x)
        plt.ylabel(y)
    elif plot_type == 'line':
        sns.lineplot(data=data, x=x, y=y)
        plt.title(f'Line Plot of {x} vs {y}')
        plt.xlabel(x)
        plt.ylabel(y)
    elif plot_type == 'box':
        sns.boxplot(data=data, y=x)
        plt.title(f'Box Plot of {x}')
        plt.ylabel(x)
    elif plot_type == 'count':
        sns.countplot(data=data, x=x)
        plt.title(f'Count Plot of {x}')
        plt.xlabel(x)
        plt.ylabel('Count')
        plt.xticks(rotation=90)
    elif plot_type == 'bar':
        sns.barplot(data=data, x=x, y=y)
        plt.title(f'Bar Plot of {x}')
        plt.xlabel(x)
        plt.ylabel(y)
        plt.xticks(rotation=90)
    elif plot_type == 'point':
        sns.pointplot(data=data, x=x, y=y)
        plt.title(f'Point Plot of {x}')
        plt.xlabel(x)
        plt.ylabel(y)
        plt.xticks(rotation=90)
    else:
        print("Invalid plot type")

    plt.show()


def encode_categorical_features(data , type_of_encoding ):
    """
    Encode categorical features using either Label Encoding or One-Hot Encoding.

    Parameters:
    -----------
    data : pandas.DataFrame
        Input data with categorical features to be encoded.
    type_of_encoding : str
        Type of encoding ('label' for Label Encoding, 'onehot' for One-Hot Encoding).

    Returns:
    --------
    pandas.DataFrame
        Data with categorical features encoded.
    
    Raises:
    -------
    ValueError
        If an unsupported encoding type is selected.
    """
    if type_of_encoding == 'label':
            label_encoder = LabelEncoder()
            X_encoded = data.copy()
            for column in X_encoded.select_dtypes(include=['object']):
                X_encoded[column] = label_encoder.fit_transform(X_encoded[column])
            return X_encoded

    

    elif type_of_encoding == 'onehot':
        # Helper function to one-hot encode categorical features
            # Create a copy of the original data
            data_encoded = data.copy()
            # Get the list of categorical columns
            categorical_columns = data.select_dtypes(include=['object']).columns
            # Apply one-hot encoding to each categorical column
            for column in categorical_columns:
                one_hot = pd.get_dummies(data_encoded[column], prefix=column)
                data_encoded = pd.concat([data_encoded, one_hot], axis=1)
                data_encoded.drop(column, axis=1, inplace=True)
            
            return data_encoded
        
    else:
        print('please choose type_of_encoding = label or onehot')

def Ashour_fun():
    #this is a test fun
    print('Hello Mr.Ashour')













                    
        

            


        