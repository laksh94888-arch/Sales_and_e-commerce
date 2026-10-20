"""
Core Analytics and Business Intelligence Module
Computes KPIs, dimensional aggregations, profitability breakdowns,
customer metrics, and dynamic data-driven business insights.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes key performance indicators (KPIs) for the sales dataset.
    Formulas:
    - Total Sales = Sum of all 'Sales'
    - Total Profit = Sum of all 'Profit'
    - Total Orders = Unique count of 'Order ID' (or total rows if Order ID absent)
    - Total Quantity = Sum of all 'Quantity' (or count of items)
    - Average Order Value (AOV) = Total Sales / Total Orders
    - Profit Margin (%) = (Total Profit / Total Sales) * 100
    - Average Discount (%) = Mean of 'Discount' * 100
    """
    if df is None or df.empty:
        return {
            "total_sales": 0.0,
            "total_profit": 0.0,
            "total_orders": 0,
            "total_quantity": 0,
            "avg_order_value": 0.0,
            "profit_margin_pct": 0.0,
            "avg_discount_pct": 0.0
        }
        
    has_sales = "Sales" in df.columns
    has_profit = "Profit" in df.columns
    has_order_id = "Order ID" in df.columns
    has_qty = "Quantity" in df.columns
    has_discount = "Discount" in df.columns
    
    total_sales = float(df["Sales"].sum()) if has_sales else 0.0
    total_profit = float(df["Profit"].sum()) if has_profit else 0.0
    
    if has_order_id:
        total_orders = int(df["Order ID"].nunique())
    else:
        total_orders = int(len(df))
        
    total_quantity = int(df["Quantity"].sum()) if has_qty else int(len(df))
    
    avg_order_value = float(total_sales / total_orders) if total_orders > 0 else 0.0
    
    profit_margin_pct = float((total_profit / total_sales) * 100) if total_sales != 0 else 0.0
    
    if has_discount:
        # Check if discount is 0-1 scale or 0-100 scale
        mean_disc = float(df["Discount"].mean())
        avg_discount_pct = mean_disc * 100 if mean_disc <= 1.0 else mean_disc
    else:
        avg_discount_pct = 0.0
        
    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "avg_order_value": round(avg_order_value, 2),
        "profit_margin_pct": round(profit_margin_pct, 2),
        "avg_discount_pct": round(avg_discount_pct, 2)
    }


def analyze_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates sales and profits by Year-Month and computes Month-over-Month (MoM) growth.
    """
    if "Order Date" not in df.columns or "Sales" not in df.columns:
        return pd.DataFrame()
        
    df_valid = df.dropna(subset=["Order Date"]).copy()
    if df_valid.empty:
        return pd.DataFrame()
        
    df_valid["YearMonth"] = df_valid["Order Date"].dt.to_period("M").astype(str)
    
    agg_dict = {"Sales": "sum"}
    if "Profit" in df_valid.columns:
        agg_dict["Profit"] = "sum"
    if "Quantity" in df_valid.columns:
        agg_dict["Quantity"] = "sum"
    if "Order ID" in df_valid.columns:
        agg_dict["Order ID"] = "nunique"
        
    monthly = df_valid.groupby("YearMonth").agg(agg_dict).reset_index()
    monthly = monthly.sort_values("YearMonth").reset_index(drop=True)
    
    if "Order ID" in monthly.columns:
        monthly.rename(columns={"Order ID": "Orders"}, inplace=True)
        
    # Calculate MoM growth for Sales
    monthly["Sales_Growth_MoM_Pct"] = monthly["Sales"].pct_change() * 100
    monthly["Sales_Growth_MoM_Pct"] = monthly["Sales_Growth_MoM_Pct"].fillna(0.0).round(2)
    
    if "Profit" in monthly.columns:
        monthly["Profit_Margin_Pct"] = np.where(
            monthly["Sales"] != 0,
            (monthly["Profit"] / monthly["Sales"]) * 100,
            0.0
        ).round(2)
        
    return monthly


def analyze_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """
    Generic aggregator for categorical dimensions (Category, Sub-Category, Region, Segment).
    """
    if dimension not in df.columns or "Sales" not in df.columns:
        return pd.DataFrame()
        
    agg_dict = {"Sales": "sum"}
    if "Profit" in df.columns:
        agg_dict["Profit"] = "sum"
    if "Quantity" in df.columns:
        agg_dict["Quantity"] = "sum"
    if "Order ID" in df.columns:
        agg_dict["Order ID"] = "nunique"
        
    result = df.groupby(dimension).agg(agg_dict).reset_index()
    
    if "Order ID" in result.columns:
        result.rename(columns={"Order ID": "Orders"}, inplace=True)
        
    if "Profit" in result.columns:
        result["Profit_Margin_Pct"] = np.where(
            result["Sales"] != 0,
            (result["Profit"] / result["Sales"]) * 100,
            0.0
        ).round(2)
        
    result = result.sort_values(by="Sales", ascending=False).reset_index(drop=True)
    return result


def analyze_discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """
    Segments transactions into discount tiers to evaluate margin erosion.
    Tiers: 0% (None), 1-10%, 11-20%, 21-30%, >30%
    """
    if "Discount" not in df.columns or "Sales" not in df.columns or "Profit" not in df.columns:
        return pd.DataFrame()
        
    df_copy = df.copy()
    disc = df_copy["Discount"]
    if disc.max() <= 1.0:
        disc_pct = disc * 100
    else:
        disc_pct = disc
        
    bins = [-1, 0.001, 10, 20, 30, 100]
    labels = ["0% (No Discount)", "1% - 10%", "11% - 20%", "21% - 30%", "> 30% Deep Discount"]
    
    df_copy["Discount_Tier"] = pd.cut(disc_pct, bins=bins, labels=labels, right=True)
    
    tier_summary = df_copy.groupby("Discount_Tier", observed=False).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Transaction_Count=("Sales", "count"),
        Avg_Discount=("Discount", lambda x: (x.mean() * 100 if x.mean() <= 1.0 else x.mean()))
    ).reset_index()
    
    tier_summary["Profit_Margin_Pct"] = np.where(
        tier_summary["Total_Sales"] != 0,
        (tier_summary["Total_Profit"] / tier_summary["Total_Sales"]) * 100,
        0.0
    ).round(2)
    
    return tier_summary


def analyze_products(df: pd.DataFrame, top_n: int = 10) -> Dict[str, pd.DataFrame]:
    """
    Identifies top products by sales, top products by profit, and loss-making products.
    """
    prod_col = "Product Name" if "Product Name" in df.columns else ("Product ID" if "Product ID" in df.columns else None)
    if not prod_col or "Sales" not in df.columns:
        return {"top_by_sales": pd.DataFrame(), "top_by_profit": pd.DataFrame(), "bottom_by_profit": pd.DataFrame()}
        
    agg_dict = {"Sales": "sum"}
    if "Profit" in df.columns:
        agg_dict["Profit"] = "sum"
    if "Quantity" in df.columns:
        agg_dict["Quantity"] = "sum"
        
    prod_summary = df.groupby(prod_col).agg(agg_dict).reset_index()
    
    if "Profit" in prod_summary.columns:
        prod_summary["Profit_Margin_Pct"] = np.where(
            prod_summary["Sales"] != 0,
            (prod_summary["Profit"] / prod_summary["Sales"]) * 100,
            0.0
        ).round(2)
        
    top_by_sales = prod_summary.sort_values(by="Sales", ascending=False).head(top_n).reset_index(drop=True)
    
    if "Profit" in prod_summary.columns:
        top_by_profit = prod_summary.sort_values(by="Profit", ascending=False).head(top_n).reset_index(drop=True)
        bottom_by_profit = prod_summary.sort_values(by="Profit", ascending=True).head(top_n).reset_index(drop=True)
    else:
        top_by_profit = pd.DataFrame()
        bottom_by_profit = pd.DataFrame()
        
    return {
        "top_by_sales": top_by_sales,
        "top_by_profit": top_by_profit,
        "bottom_by_profit": bottom_by_profit
    }


def analyze_customers(df: pd.DataFrame, top_n: int = 10) -> Dict[str, Any]:
    """
    Computes customer analytics including top clients, segment breakdown,
    and repeat purchase behavior if Customer Name or ID is available.
    """
    cust_col = "Customer Name" if "Customer Name" in df.columns else ("Customer ID" if "Customer ID" in df.columns else None)
    
    segment_df = pd.DataFrame()
    if "Segment" in df.columns and "Sales" in df.columns:
        segment_df = analyze_dimension(df, "Segment")
        
    if not cust_col or "Sales" not in df.columns:
        return {
            "top_customers": pd.DataFrame(),
            "segment_breakdown": segment_df,
            "repeat_rate_pct": 0.0,
            "total_unique_customers": 0,
            "avg_orders_per_customer": 0.0
        }
        
    agg_dict = {"Sales": "sum"}
    if "Profit" in df.columns:
        agg_dict["Profit"] = "sum"
    if "Order ID" in df.columns:
        agg_dict["Order ID"] = "nunique"
    elif "Order Date" in df.columns:
        agg_dict["Order Date"] = "count"
    else:
        agg_dict["Sales"] = ["sum", "count"]
        
    cust_summary = df.groupby(cust_col).agg(agg_dict)
    
    # Flatten MultiIndex if present
    if isinstance(cust_summary.columns, pd.MultiIndex):
        cust_summary.columns = ['_'.join(c).strip('_') for c in cust_summary.columns]
    cust_summary = cust_summary.reset_index()
    
    order_col_name = "Order ID" if "Order ID" in cust_summary.columns else ("Order Date" if "Order Date" in cust_summary.columns else None)
    
    total_custs = len(cust_summary)
    repeat_rate = 0.0
    avg_orders = 1.0
    
    if order_col_name:
        repeat_customers = cust_summary[cust_summary[order_col_name] > 1]
        repeat_rate = round((len(repeat_customers) / total_custs) * 100, 2) if total_custs > 0 else 0.0
        avg_orders = round(float(cust_summary[order_col_name].mean()), 2) if total_custs > 0 else 0.0
        cust_summary.rename(columns={order_col_name: "Orders_Count"}, inplace=True)
        
    sales_col = "Sales" if "Sales" in cust_summary.columns else [c for c in cust_summary.columns if "sales" in c.lower()][0]
    top_custs = cust_summary.sort_values(by=sales_col, ascending=False).head(top_n).reset_index(drop=True)
    
    return {
        "top_customers": top_custs,
        "segment_breakdown": segment_df,
        "repeat_rate_pct": repeat_rate,
        "total_unique_customers": total_custs,
        "avg_orders_per_customer": avg_orders
    }


def generate_business_insights(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extracts dynamic, data-driven business insights and recommendations
    directly from the actual filtered dataset.
    """
    if df is None or df.empty or "Sales" not in df.columns:
        return {"findings": ["No data available to generate insights."], "recommendations": []}
        
    findings: List[str] = []
    recommendations: List[str] = []
    
    kpis = calculate_kpis(df)
    
    # 1. Financial Performance Finding
    findings.append(
        f"Generated a total revenue of ${kpis['total_sales']:,.2f} across {kpis['total_orders']:,} orders, "
        f"achieving an overall net profit of ${kpis['total_profit']:,.2f} with an aggregate profit margin of {kpis['profit_margin_pct']:.2f}%."
    )
    
    # 2. Regional Finding
    if "Region" in df.columns and "Sales" in df.columns:
        reg_df = analyze_dimension(df, "Region")
        if not reg_df.empty:
            top_reg = reg_df.iloc[0]
            bot_reg = reg_df.iloc[-1]
            findings.append(
                f"Region '{top_reg['Region']}' is the primary revenue driver contributing ${top_reg['Sales']:,.2f} "
                f"({(top_reg['Sales']/kpis['total_sales'])*100:.1f}% of total sales), whereas '{bot_reg['Region']}' recorded the lowest volume at ${bot_reg['Sales']:,.2f}."
            )
            recommendations.append(
                f"Expand regional distribution and targeted marketing campaigns in '{top_reg['Region']}' while auditing logistics and conversion in '{bot_reg['Region']}'."
            )
            
    # 3. Category & Margin Finding
    if "Category" in df.columns and "Sales" in df.columns:
        cat_df = analyze_dimension(df, "Category")
        if not cat_df.empty:
            top_cat = cat_df.iloc[0]
            findings.append(
                f"Category '{top_cat['Category']}' leads in overall revenue with ${top_cat['Sales']:,.2f}."
            )
            if "Profit_Margin_Pct" in cat_df.columns:
                highest_margin_cat = cat_df.sort_values(by="Profit_Margin_Pct", ascending=False).iloc[0]
                lowest_margin_cat = cat_df.sort_values(by="Profit_Margin_Pct", ascending=True).iloc[0]
                findings.append(
                    f"'{highest_margin_cat['Category']}' yielded the highest profit margin at {highest_margin_cat['Profit_Margin_Pct']:.1f}%, "
                    f"while '{lowest_margin_cat['Category']}' exhibited the tightest margin at {lowest_margin_cat['Profit_Margin_Pct']:.1f}%."
                )
                if lowest_margin_cat["Profit_Margin_Pct"] < 10.0:
                    recommendations.append(
                        f"Review cost of goods sold and discount caps on '{lowest_margin_cat['Category']}' to protect baseline operating margins."
                    )
                    
    # 4. Temporal / Seasonality Finding
    if "Order Date" in df.columns:
        monthly = analyze_monthly_trends(df)
        if not monthly.empty:
            peak_month = monthly.sort_values(by="Sales", ascending=False).iloc[0]
            findings.append(
                f"Peak sales volume occurred during {peak_month['YearMonth']} reaching ${peak_month['Sales']:,.2f}."
            )
            recommendations.append(
                f"Align inventory stock and supplier lead times ahead of historical peak demand cycles observed around {peak_month['YearMonth']}."
            )
            
    # 5. Discount Impact Finding
    if "Discount" in df.columns and "Profit" in df.columns:
        tier_df = analyze_discount_impact(df)
        if not tier_df.empty:
            deep_disc = tier_df[tier_df["Discount_Tier"] == "> 30% Deep Discount"]
            no_disc = tier_df[tier_df["Discount_Tier"] == "0% (No Discount)"]
            
            if not deep_disc.empty and not no_disc.empty:
                deep_margin = deep_disc.iloc[0]["Profit_Margin_Pct"]
                no_margin = no_disc.iloc[0]["Profit_Margin_Pct"]
                findings.append(
                    f"Transactions with 0% discount preserved healthy margins of {no_margin:.1f}%, "
                    f"whereas heavy discounts (>30%) reduced average margins to {deep_margin:.1f}%."
                )
                if deep_margin < 0:
                    recommendations.append(
                        "Immediately enforce maximum discount thresholds (<20%) across loss-inducing categories to halt negative-margin transactions."
                    )
                    
    # 6. Customer Segment Finding
    if "Segment" in df.columns:
        seg_df = analyze_dimension(df, "Segment")
        if not seg_df.empty:
            top_seg = seg_df.iloc[0]
            findings.append(
                f"Customer segment '{top_seg['Segment']}' accounts for the largest share of sales (${top_seg['Sales']:,.2f})."
            )
            recommendations.append(
                f"Develop loyalty programs and personalized up-selling strategies tailored to '{top_seg['Segment']}' clients."
            )
            
    return {
        "findings": findings,
        "recommendations": recommendations
    }
