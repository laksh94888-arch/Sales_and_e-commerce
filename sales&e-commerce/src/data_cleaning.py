"""
Data Cleaning and Transformation Pipeline
Implements rigorous, non-destructive data cleaning:
- Standardizes column names
- Removes duplicates
- Imputes or handles missing values
- Converts date & numeric types cleanly
- Strips whitespace & normalizes categorical fields
- Identifies outliers via IQR without deleting valid records
- Generates comprehensive Before vs After quality audit
"""

from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np
from src.data_loader import standardize_column_names


def clean_numeric_series(series: pd.Series) -> pd.Series:
    """
    Cleans strings with currency symbols ($), commas (,), percentage signs (%),
    or financial parenthesized negatives (e.g. '(100)' -> '-100') into float numbers.
    """
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
        
    s = series.astype(str).str.strip()
    # Handle financial parentheses like (123.45)
    s = s.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    # Remove currency symbols, commas, and percentage
    s = s.str.replace("$", "", regex=False)
    s = s.str.replace(",", "", regex=False)
    s = s.str.replace("%", "", regex=False)
    return pd.to_numeric(s, errors="coerce")


def detect_outliers_iqr(series: pd.Series) -> Dict[str, Any]:
    """
    Calculates IQR bounds and count of statistical outliers for a numeric series.
    Does NOT delete records; serves for business audit and outlier flagging.
    """
    clean_s = series.dropna()
    if len(clean_s) < 4:
        return {"q1": 0.0, "q3": 0.0, "iqr": 0.0, "lower_bound": 0.0, "upper_bound": 0.0, "outlier_count": 0, "outlier_pct": 0.0}
        
    q1 = float(clean_s.quantile(0.25))
    q3 = float(clean_s.quantile(0.75))
    iqr = q3 - q1
    lower_bound = float(q1 - 1.5 * iqr)
    upper_bound = float(q3 + 1.5 * iqr)
    
    outliers = clean_s[(clean_s < lower_bound) | (clean_s > upper_bound)]
    count = int(len(outliers))
    pct = round((count / len(clean_s)) * 100, 2) if len(clean_s) > 0 else 0.0
    
    return {
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "iqr": round(iqr, 2),
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "outlier_count": count,
        "outlier_pct": pct
    }


def clean_sales_data(
    df: pd.DataFrame,
    handle_missing: str = "impute",
    remove_duplicates: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes the full data cleaning pipeline on an input DataFrame.
    Never modifies input in-place.
    
    Parameters:
        df: Input DataFrame (raw)
        handle_missing: 'impute' (median for numeric, mode/unknown for cat),
                        'drop' (drop rows with missing critical values)
        remove_duplicates: Whether to drop identical duplicate rows
        
    Returns:
        Tuple of (cleaned_df, quality_audit_dict)
    """
    if df is None or df.empty:
        raise ValueError("Cannot clean an empty or None DataFrame.")
        
    # Non-destructive copy
    df_raw = df.copy()
    initial_rows = len(df_raw)
    initial_missing = int(df_raw.isnull().sum().sum())
    initial_duplicates = int(df_raw.duplicated().sum())
    
    audit_log: List[str] = []
    
    # Step 1: Standardize column names
    cleaned, mapping = standardize_column_names(df_raw)
    if mapping:
        audit_log.append(f"Standardized {len(mapping)} column name(s): {mapping}")
        
    # Step 2: Remove duplicates if requested
    duplicates_removed = 0
    if remove_duplicates and initial_duplicates > 0:
        duplicates_removed = initial_duplicates
        cleaned = cleaned.drop_duplicates().reset_index(drop=True)
        audit_log.append(f"Removed {duplicates_removed} duplicate row(s).")
    elif initial_duplicates == 0:
        audit_log.append("No duplicate records found.")
        
    # Step 3: Strip leading/trailing whitespaces from text columns
    text_cols = cleaned.select_dtypes(include=["object"]).columns
    for col in text_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()
        # Replace empty string or 'nan' string with actual NaN
        cleaned[col] = cleaned[col].replace(["", "nan", "NaN", "None", "null"], np.nan)
        
    # Step 4: Numeric conversions
    numeric_candidates = ["Sales", "Profit", "Quantity", "Discount", "Postal Code", "Row ID"]
    for col in numeric_candidates:
        if col in cleaned.columns:
            cleaned[col] = clean_numeric_series(cleaned[col])
            audit_log.append(f"Converted '{col}' to standardized numeric format.")
            
    # Ensure Quantity is integer where possible
    if "Quantity" in cleaned.columns:
        cleaned["Quantity"] = cleaned["Quantity"].fillna(1).round().astype(int)
        
    # Step 5: Date conversions
    date_cols = [c for c in ["Order Date", "Ship Date"] if c in cleaned.columns]
    for col in date_cols:
        # Coerce to datetime format
        cleaned[col] = pd.to_datetime(cleaned[col], errors="coerce")
        nat_count = int(cleaned[col].isna().sum())
        if nat_count > 0:
            audit_log.append(f"Found {nat_count} unparseable date(s) in '{col}'.")
            
    # Drop rows where critical analytical columns (Sales or Order Date) are unparseable/null
    critical_cols = [c for c in ["Sales", "Order Date"] if c in cleaned.columns]
    if handle_missing == "drop":
        before_drop = len(cleaned)
        cleaned = cleaned.dropna(subset=critical_cols).reset_index(drop=True)
        dropped = before_drop - len(cleaned)
        if dropped > 0:
            audit_log.append(f"Dropped {dropped} row(s) missing critical analytical values ({critical_cols}).")
            
    # Step 6: Missing value imputation
    for col in cleaned.columns:
        missing_count = int(cleaned[col].isna().sum())
        if missing_count > 0:
            if col == "Discount":
                cleaned[col] = cleaned[col].fillna(0.0)
                audit_log.append(f"Filled {missing_count} missing value(s) in 'Discount' with 0.0.")
            elif col in ["Sales", "Profit"]:
                if handle_missing == "impute":
                    median_val = float(cleaned[col].median())
                    cleaned[col] = cleaned[col].fillna(median_val)
                    audit_log.append(f"Imputed {missing_count} missing value(s) in '{col}' with median ({median_val:.2f}).")
                else:
                    cleaned = cleaned.dropna(subset=[col]).reset_index(drop=True)
            elif col in ["Category", "Sub-Category", "Region", "Segment", "Ship Mode", "Country", "State", "City"]:
                cleaned[col] = cleaned[col].fillna("Unknown")
                audit_log.append(f"Imputed {missing_count} missing categorical value(s) in '{col}' with 'Unknown'.")
            elif pd.api.types.is_numeric_dtype(cleaned[col]):
                median_val = float(cleaned[col].median()) if not cleaned[col].dropna().empty else 0.0
                cleaned[col] = cleaned[col].fillna(median_val)
                audit_log.append(f"Imputed {missing_count} missing value(s) in '{col}' with median ({median_val:.2f}).")
            elif pd.api.types.is_datetime64_any_dtype(cleaned[col]):
                # Fill with forward fill or mode date if needed
                mode_date = cleaned[col].mode()[0] if not cleaned[col].dropna().empty else pd.Timestamp.now()
                cleaned[col] = cleaned[col].fillna(mode_date)
                audit_log.append(f"Filled {missing_count} missing date(s) in '{col}' with representative date.")
                
    # Step 7: Calculate Profit Margin if Sales and Profit are present
    if "Sales" in cleaned.columns and "Profit" in cleaned.columns:
        # Avoid zero division: when sales is 0, margin is 0%
        cleaned["Profit_Margin_Pct"] = np.where(
            cleaned["Sales"] != 0,
            (cleaned["Profit"] / cleaned["Sales"]) * 100,
            0.0
        ).round(2)
        
    # Step 8: Outlier Detection Summary (IQR based)
    outlier_audit = {}
    for num_col in ["Sales", "Profit", "Quantity", "Discount"]:
        if num_col in cleaned.columns:
            outlier_audit[num_col] = detect_outliers_iqr(cleaned[num_col])
            
    final_rows = len(cleaned)
    final_missing = int(cleaned.isnull().sum().sum())
    
    quality_audit = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "rows_removed": initial_rows - final_rows,
        "initial_duplicates": initial_duplicates,
        "duplicates_removed": duplicates_removed,
        "initial_missing_cells": initial_missing,
        "final_missing_cells": final_missing,
        "outlier_audit": outlier_audit,
        "audit_log": audit_log,
        "columns_before": list(df_raw.columns),
        "columns_after": list(cleaned.columns)
    }
    
    return cleaned, quality_audit
