"""
data_processing.py
------------------
Handles all data loading, cleaning, feature engineering,
and IQR-based outlier removal for P-13.

Dataset : Amazon Sales Dataset (amazon.csv)
Source  : https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset
"""

import numpy as np
import pandas as pd

# Columns Required from the Actual RAW CSV file 
REQUIRED_COLS = [
    'product_name',
    'category',
    'discounted_price',
    'actual_price',
    'discount_percentage',
    'rating',
]

DATA_PATH = 'data/amazon.csv'


def load_data(filepath: str = DATA_PATH) -> pd.DataFrame:
    """
    Load the Amazon sales CSV and keep only the required columns.

    Parameters
    ----------
    filepath : str
        Path to amazon.csv inside the data/ folder.

    Returns
    -------
    pd.DataFrame
        Raw DataFrame with only the 6 required columns.

    Raises
    ------
    FileNotFoundError
        If the CSV is not found at the given path.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Dataset not found at '{filepath}'.\n"
            "Download amazon.csv from Kaggle and place it inside the 'data/' folder.\n"
        )

    print(f"[data_processing] Loaded {len(df)} rows, {len(df.columns)} columns.")

    # Deep Copy the Required Columns for further Use
    df = df[REQUIRED_COLS].copy()
    print(f"[data_processing] Kept columns: {REQUIRED_COLS}")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean price and rating columns:
      - Strip the ₹ currency symbol and commas from price columns.
      - Convert price and rating columns to float.
      - Drop rows where discounted_price or actual_price is null/invalid.
      - Extract the top-level category (Amazon uses | as a separator).

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from load_data().

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame ready for analysis.
    """
    df = df.copy()

    # Clean the Columns and convert into numeric - $12,000 is not numeric but is an object64 needs conversion
    for col in ['discounted_price', 'actual_price']:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace('₹', '', regex=False)
            .str.replace(',', '', regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Clean the Column and convert into numeric - 74% is not numeric... It needs conversion 
    df['discount_percentage'] = (
        df['discount_percentage']
        .astype(str)
        .str.replace('%', '', regex=False)
        .str.strip()
    )
    df['discount_percentage'] = pd.to_numeric(df['discount_percentage'], errors='coerce')

    # Check if in case any of the entry in the dataset rating column is not numeric if it is then convert it!
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    # Drop the Rows where the Prices are null or partially written... 
    before = len(df)
    df.dropna(subset=['discounted_price', 'actual_price'], inplace=True)
    print(f"[data_processing] Dropped {before - len(df)} rows with null prices. Remaining: {len(df)}")

    # Extract Top-lvl Category - "Electronics|Mobile&Accessories|Chargers" --to--> "Electronics"
    df['category'] = df['category'].astype(str).str.split('|').str[0].str.strip()

    print(f"[data_processing] Unique categories: {df['category'].nunique()}")
    return df


def add_discount_amount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'discount_amount' column using vectorized Pandas operations.
    discount_amount = actual_price − discounted_price

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame from clean_data().

    Returns
    -------
    pd.DataFrame
        DataFrame with the new 'discount_amount' column added.
    """
    df = df.copy()
    df['discount_amount'] = df['actual_price'] - df['discounted_price']
    print("[data_processing] 'discount_amount' column added.")
    return df


def remove_outliers(df: pd.DataFrame, col: str = 'discounted_price') -> pd.DataFrame:
    """
    Remove extreme price outliers using the IQR method with NumPy.

    Q1 = 25th percentile, Q3 = 75th percentile
    IQR = Q3 - Q1
    Lower bound = Q1 - 1.5 * IQR
    Upper bound = Q3 + 1.5 * IQR

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the discount_amount column added.
    col : str
        Column to apply IQR filtering on (default: 'discounted_price').

    Returns
    -------
    pd.DataFrame
        DataFrame with extreme outlier rows removed.
    """
    df = df.copy()

    price_array = df[col].dropna().values

    q1 = np.percentile(price_array, 25)
    q3 = np.percentile(price_array, 75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    before = len(df)
    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    print(f"[data_processing] IQR bounds for '{col}': [{lower_bound:.2f}, {upper_bound:.2f}]")
    print(f"[data_processing] Removed {before - len(df)} outlier rows. Remaining: {len(df)}")

    return df
