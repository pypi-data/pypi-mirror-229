from setuptools import setup, find_packages

# Package metadata
NAME = 'FastML_With_EDA'
DESCRIPTION = 'This package provides a set of functions and tools for machine learning tasks, including data preprocessing, model training, and evaluation. It includes functions for loading data, exploring dataset statistics, handling missing values, detecting outliers, training machine learning models for regression or classification, and evaluating model performance.'
VERSION = '0.1.0'
AUTHOR = 'Abdelrahman Mohaemd'
AUTHOR_EMAIL = 'abdelrahman.m2922@gmail.com'
URL = 'https://github.com/Veto2922/Fast-Machine-Learning-With-EDA/tree/main'

# Packages to include
PACKAGES = find_packages(include=["FastML_With_EDA", "FastML_With_EDA.*"])

# Required dependencies
INSTALL_REQUIRES = [
    'pandas',
    'numpy',
    'scikit-learn',
    'matplotlib',
    'seaborn',
    'xgboost',
]

# # Optional dependencies
# EXTRAS_REQUIRE = {
#     'dev': ['pytest', 'flake8'],  # Example: add development/testing dependencies
# }

# # Entry point
# ENTRY_POINTS = {
#     'console_scripts': [
#         'your_script_name = your_package_name.module_name:main',  # Replace with your actual script and module name
#     ],
# }

# Package setup
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
    # extras_require=EXTRAS_REQUIRE,
    # entry_points=ENTRY_POINTS,
)
