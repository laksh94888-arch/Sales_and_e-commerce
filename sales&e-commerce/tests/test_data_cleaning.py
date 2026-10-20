"""
Tests for Data Cleaning Pipeline (src/data_cleaning.py)
Validates duplicate removal, missing value handling, date parsing,
numeric cleaning, and outlier detection.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_cleaning import clean_sales_data, clean_numeric_series, detect_outliers_iqr


@pytest.fixture
def dirty_sample_df():
    """
    Constructs a controlled synthetic dirty dataset to test cleaning mechanisms.
    """
    data = {
        "Order ID": ["CA-101", "CA-102", "CA-103", "CA-103", "CA-104", "CA-105"],
        "Order Date": ["2023-01-15", "2023-02-20", "2023-03-10", "2023-03-10", "invalid-date", "2023-05-01"],
        "Category": ["Technology", "Furniture ", np.nan, np.nan, "Office Supplies", " Technology"],
        "Sales": ["$1,200.50", "$350.00", "45.00", "45.00", "(120.00)", np.nan],
        "Quantity": ["2", "4", "1", "1", "3", "5"],
        "Discount": ["10%", "0.0", "0.20", "0.20", np.nan, "5%"],
        "Profit": ["$250.00", "-50.00", "10.00", "10.00", "(20.00)", "15.00"]
    }
    return pd.DataFrame(data)


def test_clean_numeric_series():
    """Test numeric string parsing including currency symbols, commas, percent, and parentheses."""
    s = pd.Series(["$1,250.50", "(25.00)", "10%", " 50.2 ", np.nan])
    cleaned = clean_numeric_series(s)
    
    assert cleaned.iloc[0] == 1250.50
    assert cleaned.iloc[1] == -25.00
    assert cleaned.iloc[2] == 10.0
    assert cleaned.iloc[3] == 50.2
    assert np.isnan(cleaned.iloc[4])


def test_duplicate_removal(dirty_sample_df):
    """Verify that duplicate rows are detected and removed."""
    cleaned, audit = clean_sales_data(dirty_sample_df, remove_duplicates=True)
    
    # Row CA-103 is an exact duplicate
    assert audit["initial_duplicates"] == 1
    assert audit["duplicates_removed"] == 1
    assert len(cleaned) == len(dirty_sample_df) - 1


def test_missing_values_imputation(dirty_sample_df):
    """Verify missing values are handled appropriately without destroying data."""
    cleaned, audit = clean_sales_data(dirty_sample_df, handle_missing="impute", remove_duplicates=False)
    
    # Missing category should be filled with 'Unknown'
    assert "Unknown" in cleaned["Category"].values
    
    # Missing sales should be imputed with median
    assert not cleaned["Sales"].isna().any()
    
    # Missing discount should be filled with 0.0
    assert not cleaned["Discount"].isna().any()


def test_date_conversion(dirty_sample_df):
    """Verify date columns are properly converted to datetime64."""
    cleaned, _ = clean_sales_data(dirty_sample_df)
    
    assert pd.api.types.is_datetime64_any_dtype(cleaned["Order Date"])
    assert cleaned["Order Date"].iloc[0] == pd.Timestamp("2023-01-15")


def test_whitespace_stripping(dirty_sample_df):
    """Verify leading/trailing spaces are removed from text columns."""
    cleaned, _ = clean_sales_data(dirty_sample_df)
    
    categories = cleaned["Category"].unique()
    assert "Furniture" in categories
    assert "Furniture " not in categories
    assert "Technology" in categories


def test_outlier_detection_iqr():
    """Verify IQR outlier detection detects extreme points without modifying series length."""
    # Series with standard values and one obvious outlier (10,000)
    series = pd.Series([10, 12, 14, 15, 16, 18, 19, 20, 22, 10000])
    outlier_info = detect_outliers_iqr(series)
    
    assert outlier_info["outlier_count"] == 1
    assert outlier_info["upper_bound"] < 10000
    assert outlier_info["outlier_pct"] == 10.0
