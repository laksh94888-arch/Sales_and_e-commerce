"""
Tests for Core Analytics Engine (src/analysis.py)
Validates KPI formulas, profit margin calculations, trend analysis,
and automated dynamic business insights.
"""

import pytest
import pandas as pd
import numpy as np
from src.analysis import (
    calculate_kpis,
    analyze_monthly_trends,
    analyze_dimension,
    analyze_discount_impact,
    analyze_products,
    analyze_customers,
    generate_business_insights
)


@pytest.fixture
def clean_sample_df():
    """
    Standard clean test dataset with known expected values.
    """
    data = {
        "Order ID": ["ORD-1", "ORD-1", "ORD-2", "ORD-3", "ORD-4"],
        "Order Date": pd.to_datetime(["2023-01-10", "2023-01-10", "2023-02-15", "2023-02-20", "2023-03-05"]),
        "Customer ID": ["CUST-1", "CUST-1", "CUST-2", "CUST-1", "CUST-3"],
        "Customer Name": ["Alice", "Alice", "Bob", "Alice", "Charlie"],
        "Segment": ["Consumer", "Consumer", "Corporate", "Consumer", "Home Office"],
        "Region": ["West", "West", "East", "West", "Central"],
        "Category": ["Technology", "Furniture", "Technology", "Office Supplies", "Technology"],
        "Sub-Category": ["Phones", "Chairs", "Accessories", "Paper", "Phones"],
        "Product Name": ["Phone Model X", "Office Chair Z", "USB Cable", "Copy Paper", "Phone Model Y"],
        "Sales": [1000.0, 500.0, 200.0, 100.0, 600.0],
        "Quantity": [2, 1, 4, 5, 1],
        "Discount": [0.0, 0.10, 0.0, 0.0, 0.40],
        "Profit": [200.0, -50.0, 40.0, 20.0, -100.0]
    }
    return pd.DataFrame(data)


def test_calculate_kpis_correctness(clean_sample_df):
    """Verify standard KPI formulas and metrics calculation."""
    kpis = calculate_kpis(clean_sample_df)
    
    # Expected: Total Sales = 1000 + 500 + 200 + 100 + 600 = 2400.0
    assert kpis["total_sales"] == 2400.0
    
    # Expected: Total Profit = 200 - 50 + 40 + 20 - 100 = 110.0
    assert kpis["total_profit"] == 110.0
    
    # Expected: Total Orders = ORD-1, ORD-2, ORD-3, ORD-4 = 4
    assert kpis["total_orders"] == 4
    
    # Expected: Total Quantity = 2 + 1 + 4 + 5 + 1 = 13
    assert kpis["total_quantity"] == 13
    
    # Expected: AOV = 2400 / 4 = 600.0
    assert kpis["avg_order_value"] == 600.0
    
    # Expected: Profit Margin % = (110 / 2400) * 100 = 4.58%
    assert kpis["profit_margin_pct"] == pytest.approx(4.58, rel=1e-2)


def test_calculate_kpis_zero_sales():
    """Verify edge case where Sales is 0.0 does not raise ZeroDivisionError."""
    df_zero = pd.DataFrame({
        "Sales": [0.0, 0.0],
        "Profit": [0.0, 0.0],
        "Order ID": ["O1", "O2"]
    })
    kpis = calculate_kpis(df_zero)
    assert kpis["total_sales"] == 0.0
    assert kpis["profit_margin_pct"] == 0.0
    assert kpis["avg_order_value"] == 0.0


def test_monthly_trends(clean_sample_df):
    """Verify monthly aggregation groups properly by YearMonth and calculates MoM."""
    monthly = analyze_monthly_trends(clean_sample_df)
    
    assert len(monthly) == 3  # Jan, Feb, Mar 2023
    assert list(monthly["YearMonth"]) == ["2023-01", "2023-02", "2023-03"]
    # Jan sales = 1500, Feb sales = 300, Mar sales = 600
    assert monthly.loc[monthly["YearMonth"] == "2023-01", "Sales"].iloc[0] == 1500.0
    assert monthly.loc[monthly["YearMonth"] == "2023-02", "Sales"].iloc[0] == 300.0


def test_discount_impact_analysis(clean_sample_df):
    """Verify discount tiers are created and calculate proper margins."""
    tier_df = analyze_discount_impact(clean_sample_df)
    
    assert not tier_df.empty
    # The > 30% discount row (Phone Model Y: Sales 600, Profit -100) should have negative margin
    deep_tier = tier_df[tier_df["Discount_Tier"] == "> 30% Deep Discount"]
    assert not deep_tier.empty
    assert deep_tier.iloc[0]["Profit_Margin_Pct"] < 0


def test_product_rankings(clean_sample_df):
    """Verify top products by sales and identifying loss makers."""
    prods = analyze_products(clean_sample_df, top_n=2)
    
    top_sales = prods["top_by_sales"]
    assert len(top_sales) == 2
    assert top_sales.iloc[0]["Product Name"] == "Phone Model X"
    assert top_sales.iloc[0]["Sales"] == 1000.0
    
    loss_prods = prods["bottom_by_profit"]
    assert len(loss_prods) == 2
    # Phone Model Y has profit -100
    assert loss_prods.iloc[0]["Product Name"] == "Phone Model Y"
    assert loss_prods.iloc[0]["Profit"] == -100.0


def test_customer_repeat_rate(clean_sample_df):
    """Verify repeat customer detection (Alice has 2 distinct orders: ORD-1 and ORD-3)."""
    cust_res = analyze_customers(clean_sample_df)
    
    # Alice (2 orders), Bob (1 order), Charlie (1 order) -> 1 out of 3 is repeat
    assert cust_res["total_unique_customers"] == 3
    assert cust_res["repeat_rate_pct"] == pytest.approx(33.33, rel=1e-2)


def test_dynamic_business_insights(clean_sample_df):
    """Verify dynamic generation of business insights from dataset."""
    insights = generate_business_insights(clean_sample_df)
    
    assert "findings" in insights
    assert "recommendations" in insights
    assert len(insights["findings"]) >= 3
    assert len(insights["recommendations"]) >= 1
    
    # Check that findings mention revenue and profit
    joined_findings = " ".join(insights["findings"])
    assert "$2,400.00" in joined_findings
    assert "$110.00" in joined_findings
