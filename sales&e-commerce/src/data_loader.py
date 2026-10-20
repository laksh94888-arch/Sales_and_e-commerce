"""
Data Loader and Validator Module
Handles ingestion of CSV and Excel files, standardizes column mappings,
and validates datasets against analytical requirements.
"""

import io
import os
from typing import Tuple, Dict, Any, Union, Optional
import pandas as pd
import numpy as np

# Canonical analytical columns and their typical variations
COLUMN_SYNONYMS: Dict[str, list] = {
    "Order ID": ["order_id", "orderid", "order id", "invoice_no", "invoice no", "transaction_id"],
    "Order Date": ["order_date", "orderdate", "order date", "date", "invoice_date", "invoicedate"],
    "Ship Date": ["ship_date", "shipdate", "ship date", "shipping_date"],
    "Ship Mode": ["ship_mode", "shipmode", "ship mode", "shipping_mode"],
    "Customer ID": ["customer_id", "customerid", "customer id", "client_id"],
    "Customer Name": ["customer_name", "customername", "customer name", "client_name", "customer"],
    "Segment": ["segment", "customer_segment", "customer segment", "market_segment"],
    "Country": ["country", "nation"],
    "City": ["city", "town"],
    "State": ["state", "province", "region_state"],
    "Postal Code": ["postal_code", "postalcode", "postal code", "zip", "zip_code", "zipcode"],
    "Region": ["region", "territory", "zone", "area"],
    "Product ID": ["product_id", "productid", "product id", "item_id", "sku"],
    "Category": ["category", "product_category", "product category"],
    "Sub-Category": ["sub-category", "sub_category", "subcategory", "sub category", "product_sub_category"],
    "Product Name": ["product_name", "productname", "product name", "item_name", "product", "description"],
    "Sales": ["sales", "revenue", "sales_amount", "sales amount", "total_sales", "turnover", "amount"],
    "Quantity": ["quantity", "qty", "quantity_sold", "units", "units_sold"],
    "Discount": ["discount", "discount_rate", "discount_amount", "discount_pct"],
    "Profit": ["profit", "net_profit", "earnings", "margin_amount", "profit_loss"]
}


def standardize_column_names(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Standardize DataFrame column names by stripping whitespace and mapping
    common aliases to canonical column names.
    
    Returns:
        Tuple of (renamed_dataframe, mapping_applied)
    """
    df_copy = df.copy()
    # Strip whitespace from column names
    df_copy.columns = [str(c).strip() for c in df_copy.columns]
    
    mapping: Dict[str, str] = {}
    lower_to_orig = {col.lower().replace("-", " ").replace("_", " "): col for col in df_copy.columns}
    
    for canonical, synonyms in COLUMN_SYNONYMS.items():
        # First check direct exact match (case-insensitive)
        matched = False
        for syn in [canonical] + synonyms:
            clean_syn = syn.lower().replace("-", " ").replace("_", " ")
            if clean_syn in lower_to_orig:
                orig_col = lower_to_orig[clean_syn]
                mapping[orig_col] = canonical
                matched = True
                break
        if matched:
            continue
            
    df_copy.rename(columns=mapping, inplace=True)
    return df_copy, mapping


def load_dataset(file_source: Union[str, io.BytesIO, Any], file_name: Optional[str] = None) -> pd.DataFrame:
    """
    Load a dataset from a file path or file-like buffer (CSV or Excel).
    Tries multiple encodings for CSV files.
    """
    name = ""
    if isinstance(file_source, str):
        name = file_source.lower()
    elif file_name:
        name = file_name.lower()
    elif hasattr(file_source, "name"):
        name = getattr(file_source, "name").lower()
        
    is_excel = name.endswith(".xlsx") or name.endswith(".xls")
    
    if is_excel:
        return pd.read_excel(file_source)
    else:
        # CSV parsing with encoding fallback
        encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
        last_error = None
        for enc in encodings:
            try:
                if hasattr(file_source, "seek"):
                    file_source.seek(0)
                return pd.read_csv(file_source, encoding=enc)
            except Exception as e:
                last_error = e
                continue
        raise ValueError(f"Failed to load CSV file with supported encodings: {last_error}")


def validate_dataset(df: pd.DataFrame, min_rows: int = 10, min_cols: int = 5) -> Dict[str, Any]:
    """
    Validate the dataset against academic and analytical standards.
    Checks row count, column count, missing values, duplicates, and column availability.
    """
    errors = []
    warnings = []
    
    if df is None or df.empty:
        return {
            "is_valid": False,
            "errors": ["Dataset is completely empty."],
            "warnings": [],
            "stats": {"rows": 0, "columns": 0},
            "columns": []
        }
        
    num_rows, num_cols = df.shape
    
    if num_rows < min_rows:
        errors.append(f"Dataset has only {num_rows} rows. Minimum required is {min_rows}.")
    elif num_rows < 500:
        warnings.append(f"Dataset has {num_rows} rows. College guidelines recommend at least 500 records.")
        
    if num_cols < min_cols:
        errors.append(f"Dataset has only {num_cols} columns. Minimum required is {min_cols}.")
    elif num_cols < 10:
        warnings.append(f"Dataset has {num_cols} columns. College guidelines recommend at least 10 features.")
        
    # Standardize copy to check canonical analytical columns
    std_df, _ = standardize_column_names(df)
    cols = list(std_df.columns)
    
    # Check essential column: Sales is mandatory for a sales analytics dashboard
    if "Sales" not in cols:
        errors.append("Critical column missing: 'Sales' (or equivalent 'Revenue', 'Amount').")
        
    # Check recommended analytical columns
    recommended_cols = ["Profit", "Order Date", "Category", "Region", "Quantity", "Discount"]
    missing_rec = [c for c in recommended_cols if c not in cols]
    if missing_rec:
        warnings.append(f"Optional analytical columns missing: {', '.join(missing_rec)}. Associated charts will be disabled.")
        
    # Duplicate and missing stats
    dup_count = int(df.duplicated().sum())
    missing_by_col = df.isnull().sum().to_dict()
    total_missing = int(df.isnull().sum().sum())
    missing_pct = round((total_missing / (num_rows * num_cols)) * 100, 2) if num_rows > 0 and num_cols > 0 else 0
    
    data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    is_valid = len(errors) == 0
    
    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "rows": num_rows,
            "columns": num_cols,
            "duplicates": dup_count,
            "total_missing_cells": total_missing,
            "missing_percentage": missing_pct,
            "missing_by_column": missing_by_col,
            "data_types": data_types
        },
        "columns": cols,
        "standardized_columns": list(std_df.columns)
    }
