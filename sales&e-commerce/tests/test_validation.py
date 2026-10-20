"""
Tests for Data Validation and Schema Standards (src/data_loader.py)
Validates row/column bounds, required columns, and schema resiliency.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_loader import validate_dataset, standardize_column_names


def test_empty_dataframe_validation():
    """Verify empty DataFrame returns is_valid=False with clear error."""
    empty_df = pd.DataFrame()
    val = validate_dataset(empty_df)
    
    assert val["is_valid"] is False
    assert any("empty" in err.lower() for err in val["errors"])


def test_minimum_rows_and_columns_check():
    """Verify validation triggers errors when below hard thresholds."""
    tiny_df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    val = validate_dataset(tiny_df, min_rows=5, min_cols=3)
    
    assert val["is_valid"] is False
    assert any("rows" in err for err in val["errors"])
    assert any("columns" in err for err in val["errors"])


def test_college_guidelines_warnings():
    """Verify warnings are emitted when dataset is below college 500-row or 10-column guidelines."""
    # 20 rows, 6 columns
    df_small = pd.DataFrame({
        f"col_{i}": np.random.randn(20) for i in range(6)
    })
    df_small["Sales"] = 100.0  # provide sales so not invalid
    
    val = validate_dataset(df_small, min_rows=10, min_cols=5)
    # Should be valid (meets hard min), but have warnings for college 500 rows and 10 cols
    assert val["is_valid"] is True
    assert any("500 records" in warn for warn in val["warnings"])
    assert any("10 features" in warn for warn in val["warnings"])


def test_missing_sales_column_error():
    """Verify missing Sales column produces a validation error."""
    df_no_sales = pd.DataFrame({
        "Order Date": ["2023-01-01"] * 15,
        "Category": ["Tech"] * 15,
        "Region": ["East"] * 15,
        "Profit": [10.0] * 15,
        "Quantity": [1] * 15
    })
    val = validate_dataset(df_no_sales)
    
    assert val["is_valid"] is False
    assert any("Sales" in err for err in val["errors"])


def test_column_standardization_aliases():
    """Verify common alias variants (e.g. revenue, order_date) are properly mapped to canonical names."""
    df_aliases = pd.DataFrame({
        "order_date": ["2023-01-01"],
        "revenue": [500.0],
        "net_profit": [100.0],
        "qty": [2],
        "product_category": ["Furniture"]
    })
    
    std_df, mapping = standardize_column_names(df_aliases)
    
    assert "Sales" in std_df.columns
    assert "Order Date" in std_df.columns
    assert "Profit" in std_df.columns
    assert "Quantity" in std_df.columns
    assert "Category" in std_df.columns
    assert mapping["revenue"] == "Sales"
