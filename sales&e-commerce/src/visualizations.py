"""
Interactive Data Visualizations Module
Builds responsive, executive-ready Plotly charts for Streamlit.
Adheres to cohesive visual hierarchy, clean color palettes, and legible typography.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Cohesive Executive Color Palette
PRIMARY_COLOR = "#4F46E5"    # Indigo
SECONDARY_COLOR = "#06B6D4"  # Cyan
SUCCESS_COLOR = "#10B981"    # Emerald
DANGER_COLOR = "#EF4444"     # Rose/Red
WARNING_COLOR = "#F59E0B"    # Amber
NEUTRAL_COLOR = "#64748B"    # Slate
BG_COLOR = "rgba(0,0,0,0)"

BASE_LAYOUT = dict(
    paper_bgcolor=BG_COLOR,
    plot_bgcolor=BG_COLOR,
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size=12),
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor="#1E293B", font_size=12, font_color="#FFFFFF")
)


def plot_monthly_trend(df_monthly: pd.DataFrame) -> go.Figure:
    """
    Renders monthly sales and profit trend with dual-axis or stacked markers.
    """
    if df_monthly.empty:
        fig = go.Figure()
        fig.add_annotation(text="No monthly trend data available", showarrow=False)
        return fig
        
    fig = go.Figure()
    
    # Sales line/area
    fig.add_trace(go.Scatter(
        x=df_monthly["YearMonth"],
        y=df_monthly["Sales"],
        name="Sales ($)",
        mode="lines+markers",
        line=dict(color=PRIMARY_COLOR, width=3),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.2f}<extra></extra>"
    ))
    
    if "Profit" in df_monthly.columns:
        fig.add_trace(go.Scatter(
            x=df_monthly["YearMonth"],
            y=df_monthly["Profit"],
            name="Profit ($)",
            mode="lines+markers",
            line=dict(color=SUCCESS_COLOR, width=2.5, dash="dot"),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>"
        ))
        
    fig.update_layout(
        **BASE_LAYOUT,
        title="<b>Monthly Sales & Profit Performance Trend</b>",
        xaxis=dict(title="Month", tickangle=-45, showgrid=True, gridcolor="rgba(150,150,150,0.15)"),
        yaxis=dict(title="Amount ($USD)", showgrid=True, gridcolor="rgba(150,150,150,0.15)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_category_sales_profit(df_cat: pd.DataFrame) -> go.Figure:
    """
    Grouped bar chart comparing Sales and Profit across Product Categories.
    """
    if df_cat.empty:
        fig = go.Figure()
        fig.add_annotation(text="No category data available", showarrow=False)
        return fig
        
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_cat["Category"],
        y=df_cat["Sales"],
        name="Total Sales",
        marker_color=PRIMARY_COLOR,
        hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.2f}<extra></extra>"
    ))
    
    if "Profit" in df_cat.columns:
        fig.add_trace(go.Bar(
            x=df_cat["Category"],
            y=df_cat["Profit"],
            name="Total Profit",
            marker_color=SUCCESS_COLOR,
            hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>"
        ))
        
    fig.update_layout(
        **BASE_LAYOUT,
        barmode="group",
        title="<b>Sales vs. Profit by Category</b>",
        xaxis=dict(title="Category", showgrid=False),
        yaxis=dict(title="Amount ($USD)", showgrid=True, gridcolor="rgba(150,150,150,0.15)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_subcategory_profitability(df_sub: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart of Sub-Categories sorted by profit, colored by positive/loss.
    """
    if df_sub.empty:
        fig = go.Figure()
        fig.add_annotation(text="No subcategory data available", showarrow=False)
        return fig
        
    df_sorted = df_sub.sort_values(by="Profit" if "Profit" in df_sub.columns else "Sales", ascending=True)
    
    if "Profit" in df_sorted.columns:
        colors = [SUCCESS_COLOR if p >= 0 else DANGER_COLOR for p in df_sorted["Profit"]]
        val_col = "Profit"
        title_text = "<b>Sub-Category Net Profit / Loss Breakdown</b>"
        hover = "<b>%{y}</b><br>Profit: $%{x:,.2f}<extra></extra>"
    else:
        colors = PRIMARY_COLOR
        val_col = "Sales"
        title_text = "<b>Sub-Category Sales Breakdown</b>"
        hover = "<b>%{y}</b><br>Sales: $%{x:,.2f}<extra></extra>"
        
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted["Sub-Category"],
        x=df_sorted[val_col],
        orientation="h",
        marker_color=colors,
        hovertemplate=hover
    ))
    
    fig.update_layout(
        **BASE_LAYOUT,
        title=title_text,
        xaxis=dict(title="Profit ($USD)" if val_col == "Profit" else "Sales ($USD)", showgrid=True, gridcolor="rgba(150,150,150,0.15)"),
        yaxis=dict(title="Sub-Category", showgrid=False)
    )
    return fig


def plot_regional_breakdown(df_region: pd.DataFrame) -> go.Figure:
    """
    Bar chart showing Sales and Profit by geographic Region.
    """
    if df_region.empty:
        fig = go.Figure()
        fig.add_annotation(text="No regional data available", showarrow=False)
        return fig
        
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_region["Region"],
        y=df_region["Sales"],
        name="Sales",
        marker_color=SECONDARY_COLOR,
        hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.2f}<extra></extra>"
    ))
    
    if "Profit" in df_region.columns:
        fig.add_trace(go.Bar(
            x=df_region["Region"],
            y=df_region["Profit"],
            name="Profit",
            marker_color=SUCCESS_COLOR,
            hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>"
        ))
        
    fig.update_layout(
        **BASE_LAYOUT,
        barmode="group",
        title="<b>Regional Sales & Profit Comparison</b>",
        xaxis=dict(title="Region"),
        yaxis=dict(title="Amount ($USD)", showgrid=True, gridcolor="rgba(150,150,150,0.15)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_discount_vs_margin(df_tier: pd.DataFrame) -> go.Figure:
    """
    Bar chart depicting how increasing discount brackets erode operating profit margins.
    """
    if df_tier.empty:
        fig = go.Figure()
        fig.add_annotation(text="No discount tier data available", showarrow=False)
        return fig
        
    colors = [SUCCESS_COLOR if m >= 15 else (WARNING_COLOR if m >= 0 else DANGER_COLOR) for m in df_tier["Profit_Margin_Pct"]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_tier["Discount_Tier"].astype(str),
        y=df_tier["Profit_Margin_Pct"],
        marker_color=colors,
        text=df_tier["Profit_Margin_Pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="<b>Tier: %{x}</b><br>Profit Margin: %{y:.2f}%<br>Sales: $%{customdata[0]:,.2f}<extra></extra>",
        customdata=df_tier[["Total_Sales"]]
    ))
    
    fig.update_layout(
        **BASE_LAYOUT,
        title="<b>Operating Profit Margin (%) by Discount Tier</b>",
        xaxis=dict(title="Discount Bracket"),
        yaxis=dict(title="Profit Margin (%)", showgrid=True, gridcolor="rgba(150,150,150,0.15)"),
    )
    return fig


def plot_top_products_bar(df_prod: pd.DataFrame, metric: str = "Sales", top_n: int = 10) -> go.Figure:
    """
    Horizontal bar chart for top products by Sales or Profit.
    """
    if df_prod.empty:
        fig = go.Figure()
        fig.add_annotation(text="No product performance data available", showarrow=False)
        return fig
        
    col_name = "Product Name" if "Product Name" in df_prod.columns else "Product ID"
    df_sorted = df_prod.head(top_n).sort_values(by=metric, ascending=True)
    
    bar_color = PRIMARY_COLOR if metric == "Sales" else (SUCCESS_COLOR if df_sorted[metric].min() >= 0 else DANGER_COLOR)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted[col_name].apply(lambda s: (str(s)[:35] + "...") if len(str(s)) > 35 else str(s)),
        x=df_sorted[metric],
        orientation="h",
        marker_color=bar_color,
        hovertemplate="<b>%{y}</b><br>" + metric + ": $%{x:,.2f}<extra></extra>"
    ))
    
    fig.update_layout(
        **BASE_LAYOUT,
        title=f"<b>Top {top_n} Products by {metric}</b>",
        xaxis=dict(title=f"{metric} ($USD)", showgrid=True, gridcolor="rgba(150,150,150,0.15)"),
        yaxis=dict(title="Product", showgrid=False)
    )
    return fig


def plot_customer_segment_donut(df_segment: pd.DataFrame) -> go.Figure:
    """
    Donut chart of sales distribution by Customer Segment.
    """
    if df_segment.empty or "Segment" not in df_segment.columns:
        fig = go.Figure()
        fig.add_annotation(text="No segment data available", showarrow=False)
        return fig
        
    fig = go.Figure(data=[go.Pie(
        labels=df_segment["Segment"],
        values=df_segment["Sales"],
        hole=0.55,
        marker=dict(colors=[PRIMARY_COLOR, SECONDARY_COLOR, WARNING_COLOR, SUCCESS_COLOR]),
        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        **BASE_LAYOUT,
        title="<b>Sales Share by Customer Segment</b>",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig


def plot_missing_values_bar(missing_dict: Dict[str, int]) -> go.Figure:
    """
    Bar chart summarizing missing/null values across all columns.
    """
    cols = list(missing_dict.keys())
    counts = [missing_dict[c] for c in cols]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cols,
        y=counts,
        marker_color=[DANGER_COLOR if c > 0 else SUCCESS_COLOR for c in counts],
        hovertemplate="<b>%{x}</b><br>Missing Values: %{y}<extra></extra>"
    ))
    
    fig.update_layout(
        **BASE_LAYOUT,
        title="<b>Missing Values Count by Column</b>",
        xaxis=dict(title="Column", tickangle=-45),
        yaxis=dict(title="Null Count", showgrid=True, gridcolor="rgba(150,150,150,0.15)")
    )
    return fig
