"""
Sales & E-Commerce Performance Analytics Dashboard
An interactive, enterprise-grade Streamlit application for sales data analytics,
cleaning, visualization, automated business insights, and executive PDF reporting.
"""

import io
import os
import pandas as pd
import numpy as np
import streamlit as st

from src.data_loader import load_dataset, validate_dataset, standardize_column_names
from src.data_cleaning import clean_sales_data
from src.analysis import (
    calculate_kpis,
    analyze_monthly_trends,
    analyze_dimension,
    analyze_discount_impact,
    analyze_products,
    analyze_customers,
    generate_business_insights
)
from src.visualizations import (
    plot_monthly_trend,
    plot_category_sales_profit,
    plot_subcategory_profitability,
    plot_regional_breakdown,
    plot_discount_vs_margin,
    plot_top_products_bar,
    plot_customer_segment_donut,
    plot_missing_values_bar
)
from src.report_generator import generate_pdf_report

# Page Configuration
st.set_page_config(
    page_title="Sales & E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Executive CSS Styling
st.markdown("""
<style>
    /* Global Typography & Background Adjustments */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #FFFFFF;
    }
    .main-header p {
        margin: 6px 0 0 0;
        font-size: 14px;
        color: #C7D2FE;
    }
    
    /* Executive Metric Card */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border-top: 4px solid #4F46E5;
        margin-bottom: 15px;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 11px;
        color: #94A3B8;
        margin-top: 2px;
    }
    
    /* Pill Badges */
    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-blue { background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE; }
    .badge-green { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
    .badge-amber { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
    
    /* Section Card */
    .content-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def get_bundled_dataset() -> pd.DataFrame:
    """Loads the genuine Sample Superstore dataset from local storage."""
    file_path = os.path.join("data", "sample_sales_data.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"Sample dataset file not found at {file_path}.")
        return pd.DataFrame()


# ----------------------------------------------------
# SIDEBAR CONTROLS & NAVIGATION
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### 📊 Control Center")
    
    # Dataset Selection
    data_source_mode = st.radio(
        "Select Data Source:",
        ["Bundled Superstore Dataset", "Upload Custom File (CSV/XLSX)"],
        index=0
    )
    
    raw_df = None
    source_label = ""
    
    if data_source_mode == "Bundled Superstore Dataset":
        raw_df = get_bundled_dataset()
        source_label = "Superstore Sales Dataset (Tableau Genuine Sample, 9,994 records)"
        st.caption("✅ Loaded default Superstore dataset.")
    else:
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])
        if uploaded_file is not None:
            try:
                raw_df = load_dataset(uploaded_file, file_name=uploaded_file.name)
                source_label = f"Uploaded File: {uploaded_file.name}"
                st.success(f"File loaded: {uploaded_file.name} ({len(raw_df):,} rows)")
            except Exception as e:
                st.error(f"Error loading file: {e}")
                raw_df = None
        else:
            st.info("Please upload a CSV or Excel file or switch back to the bundled dataset.")
            raw_df = None

    st.markdown("---")
    
    # Cleaning Pipeline Options
    st.markdown("#### ⚙️ Data Preprocessing")
    cleaning_mode = st.selectbox(
        "Missing Values Strategy:",
        ["impute", "drop"],
        format_func=lambda x: "Impute (Median for numeric, 'Unknown' for text)" if x == "impute" else "Drop rows with missing critical values"
    )
    remove_dups = st.checkbox("Remove Duplicate Records", value=True)

# Stop early if raw_df is absent
if raw_df is None or raw_df.empty:
    st.warning("⚠️ No dataset loaded. Please select the bundled dataset or upload a file.")
    st.stop()

# Validate the raw dataset
val_results = validate_dataset(raw_df)

# Execute Data Cleaning Pipeline
cleaned_df, quality_audit = clean_sales_data(
    raw_df,
    handle_missing=cleaning_mode,
    remove_duplicates=remove_dups
)

# ----------------------------------------------------
# DYNAMIC SIDEBAR FILTERS
# ----------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("#### 🔍 Filter Controls")
    
    filtered_df = cleaned_df.copy()
    filter_applied_notes = []
    
    # 1. Date Range Filter
    if "Order Date" in filtered_df.columns and pd.api.types.is_datetime64_any_dtype(filtered_df["Order Date"]):
        valid_dates = filtered_df["Order Date"].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            if min_date < max_date:
                date_range = st.date_input(
                    "Order Date Range:",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start_d, end_d = date_range
                    filtered_df = filtered_df[
                        (filtered_df["Order Date"].dt.date >= start_d) & 
                        (filtered_df["Order Date"].dt.date <= end_d)
                    ]
                    filter_applied_notes.append(f"Date: {start_d} to {end_d}")
                    
    # 2. Region Filter
    if "Region" in filtered_df.columns:
        all_regions = sorted(filtered_df["Region"].dropna().unique().tolist())
        selected_regions = st.multiselect("Region:", options=all_regions, default=[])
        if selected_regions:
            filtered_df = filtered_df[filtered_df["Region"].isin(selected_regions)]
            filter_applied_notes.append(f"Regions: {', '.join(selected_regions)}")
            
    # 3. Category Filter
    if "Category" in filtered_df.columns:
        all_categories = sorted(filtered_df["Category"].dropna().unique().tolist())
        selected_categories = st.multiselect("Category:", options=all_categories, default=[])
        if selected_categories:
            filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]
            filter_applied_notes.append(f"Categories: {', '.join(selected_categories)}")
            
    # 4. Sub-Category Filter (dynamically filtered by selected Category)
    if "Sub-Category" in filtered_df.columns:
        all_subcategories = sorted(filtered_df["Sub-Category"].dropna().unique().tolist())
        selected_subcategories = st.multiselect("Sub-Category:", options=all_subcategories, default=[])
        if selected_subcategories:
            filtered_df = filtered_df[filtered_df["Sub-Category"].isin(selected_subcategories)]
            filter_applied_notes.append(f"Sub-Categories: {len(selected_subcategories)} selected")
            
    # 5. Customer Segment Filter
    if "Segment" in filtered_df.columns:
        all_segments = sorted(filtered_df["Segment"].dropna().unique().tolist())
        selected_segments = st.multiselect("Segment:", options=all_segments, default=[])
        if selected_segments:
            filtered_df = filtered_df[filtered_df["Segment"].isin(selected_segments)]
            filter_applied_notes.append(f"Segments: {', '.join(selected_segments)}")

    # Reset Filters Button
    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()

    st.markdown("---")
    # Sidebar Navigation Menu
    nav_page = st.radio(
        "📌 Navigation Menu:",
        [
            "📊 Executive Overview",
            "📈 Sales & Trends",
            "💰 Profitability & Discounts",
            "📦 Product Analytics",
            "👥 Customer Insights",
            "🧠 Business Insights",
            "🧹 Data Quality Audit",
            "📥 Export & PDF Report"
        ]
    )

# ----------------------------------------------------
# MAIN DASHBOARD HEADER
# ----------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>SALES & E-COMMERCE PERFORMANCE ANALYTICS</h1>
    <p>Transforming raw sales data into actionable business insights & executive intelligence.</p>
</div>
""", unsafe_allow_html=True)

# Active Filters Summary Bar
active_filter_str = " | ".join(filter_applied_notes) if filter_applied_notes else "Showing all records (No filters applied)"
st.markdown(
    f"<div style='margin-bottom: 16px; font-size: 13px; color: #475569;'>"
    f"<b>Scope:</b> <span class='badge-pill badge-blue'>{source_label}</span> "
    f"<span class='badge-pill badge-green'>{len(filtered_df):,} records active</span> "
    f"<span class='badge-pill badge-amber'>{active_filter_str}</span>"
    f"</div>",
    unsafe_allow_html=True
)

# Handle Empty Filter Results Gracefully
if filtered_df.empty:
    st.error("⚠️ No transactions match the selected filter combination. Please broaden your filter parameters or click 'Reset All Filters'.")
    st.stop()

# Compute Analytics & KPIs
kpis = calculate_kpis(filtered_df)
monthly_df = analyze_monthly_trends(filtered_df)
category_df = analyze_dimension(filtered_df, "Category") if "Category" in filtered_df.columns else pd.DataFrame()
subcategory_df = analyze_dimension(filtered_df, "Sub-Category") if "Sub-Category" in filtered_df.columns else pd.DataFrame()
region_df = analyze_dimension(filtered_df, "Region") if "Region" in filtered_df.columns else pd.DataFrame()
discount_tier_df = analyze_discount_impact(filtered_df) if "Discount" in filtered_df.columns else pd.DataFrame()
products_dict = analyze_products(filtered_df, top_n=10)
customers_dict = analyze_customers(filtered_df, top_n=10)
insights_dict = generate_business_insights(filtered_df)


# ----------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# ----------------------------------------------------
if nav_page == "📊 Executive Overview":
    st.markdown("### 📊 Executive Overview & KPI Scorecard")
    
    # 6 Core KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">${kpis['total_sales']:,.2f}</div>
            <div class="metric-sub">Sum of all sales transactions</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        profit_color = "#10B981" if kpis['total_profit'] >= 0 else "#EF4444"
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: {profit_color};">
            <div class="metric-label">Net Profit</div>
            <div class="metric-value" style="color: {profit_color};">${kpis['total_profit']:,.2f}</div>
            <div class="metric-sub">Cumulative bottom line</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #06B6D4;">
            <div class="metric-label">Profit Margin</div>
            <div class="metric-value">{kpis['profit_margin_pct']:.2f}%</div>
            <div class="metric-sub">(Net Profit ÷ Sales) × 100</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #8B5CF6;">
            <div class="metric-label">Total Orders</div>
            <div class="metric-value">{kpis['total_orders']:,}</div>
            <div class="metric-sub">Unique invoices/orders</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #F59E0B;">
            <div class="metric-label">Units Sold</div>
            <div class="metric-value">{kpis['total_quantity']:,}</div>
            <div class="metric-sub">Total product units</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col6:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #EC4899;">
            <div class="metric-label">Avg Order Value</div>
            <div class="metric-value">${kpis['avg_order_value']:,.2f}</div>
            <div class="metric-sub">Revenue ÷ Total Orders</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Top Visualizations for Overview
    row1_col1, row1_col2 = st.columns([3, 2])
    with row1_col1:
        if not monthly_df.empty:
            st.plotly_chart(plot_monthly_trend(monthly_df), use_container_width=True)
        else:
            st.info("Order Date column unavailable for monthly trend chart.")
            
    with row1_col2:
        if not category_df.empty:
            st.plotly_chart(plot_category_sales_profit(category_df), use_container_width=True)
        else:
            st.info("Category column unavailable for category breakdown.")

    # High-level Quick Insights Callout
    with st.expander("💡 Instant Executive Summary & Metric Definitions", expanded=True):
        st.markdown("""
        - **Total Sales**: Total gross revenue generated across all transactions before operational deductions.
        - **Net Profit**: Cumulative earnings remaining after deducting standard product costs.
        - **Profit Margin (%)**: Percentage of revenue converted into net profit. `(Profit / Sales) * 100`.
        - **Average Order Value (AOV)**: Average dollar amount spent per transaction order. `Sales / Total Orders`.
        - **Units Sold**: Aggregate physical quantity of items delivered to customers.
        """)


# ----------------------------------------------------
# PAGE 2: SALES & GEOGRAPHIC ANALYSIS
# ----------------------------------------------------
elif nav_page == "📈 Sales & Trends":
    st.markdown("### 📈 Sales Performance & Geographic Distribution")
    
    tab1, tab2 = st.tabs(["📅 Temporal Trend & MoM Growth", "🗺️ Geographic & Regional Breakdown"])
    
    with tab1:
        if not monthly_df.empty:
            st.plotly_chart(plot_monthly_trend(monthly_df), use_container_width=True)
            
            st.markdown("#### Monthly Performance Summary Table")
            display_monthly = monthly_df.copy()
            st.dataframe(
                display_monthly.style.format({
                    "Sales": "${:,.2f}",
                    "Profit": "${:,.2f}",
                    "Profit_Margin_Pct": "{:.2f}%",
                    "Sales_Growth_MoM_Pct": "{:+.2f}%"
                }),
                use_container_width=True
            )
        else:
            st.warning("Temporal analysis requires an 'Order Date' column.")
            
    with tab2:
        c1, c2 = st.columns([1, 1])
        with c1:
            if not region_df.empty:
                st.plotly_chart(plot_regional_breakdown(region_df), use_container_width=True)
            else:
                st.info("Region column unavailable.")
                
        with c2:
            if "State" in filtered_df.columns:
                state_df = analyze_dimension(filtered_df, "State").head(10)
                st.markdown("#### Top 10 States by Sales")
                st.dataframe(
                    state_df.style.format({
                        "Sales": "${:,.2f}",
                        "Profit": "${:,.2f}",
                        "Profit_Margin_Pct": "{:.2f}%"
                    }),
                    use_container_width=True
                )
            else:
                st.info("State column unavailable.")


# ----------------------------------------------------
# PAGE 3: PROFITABILITY & DISCOUNTS
# ----------------------------------------------------
elif nav_page == "💰 Profitability & Discounts":
    st.markdown("### 💰 Profitability & Discount Sensitivity Analysis")
    
    st.markdown("""
    Examine which business sectors yield the healthiest returns and observe how aggressive
    discount policies directly erode bottom-line operational margins.
    """)
    
    c1, c2 = st.columns([1, 1])
    with c1:
        if not subcategory_df.empty:
            st.plotly_chart(plot_subcategory_profitability(subcategory_df), use_container_width=True)
        else:
            st.info("Sub-Category data not present in dataset.")
            
    with c2:
        if not discount_tier_df.empty:
            st.plotly_chart(plot_discount_vs_margin(discount_tier_df), use_container_width=True)
        else:
            st.info("Discount data not available in dataset.")
            
    if not discount_tier_df.empty:
        st.markdown("#### Discount Tier Margin Breakdown Table")
        st.dataframe(
            discount_tier_df.style.format({
                "Total_Sales": "${:,.2f}",
                "Total_Profit": "${:,.2f}",
                "Transaction_Count": "{:,}",
                "Avg_Discount": "{:.2f}%",
                "Profit_Margin_Pct": "{:+.2f}%"
            }),
            use_container_width=True
        )


# ----------------------------------------------------
# PAGE 4: PRODUCT ANALYTICS
# ----------------------------------------------------
elif nav_page == "📦 Product Analytics":
    st.markdown("### 📦 Product & Catalog Performance")
    
    p1, p2 = st.columns([1, 1])
    with p1:
        st.plotly_chart(plot_top_products_bar(products_dict["top_by_sales"], metric="Sales", top_n=10), use_container_width=True)
    with p2:
        if not products_dict["top_by_profit"].empty:
            st.plotly_chart(plot_top_products_bar(products_dict["top_by_profit"], metric="Profit", top_n=10), use_container_width=True)
            
    # Bottom Products / Loss Makers
    if not products_dict["bottom_by_profit"].empty:
        st.markdown("#### ⚠️ Top Loss-Making Products (Margin Detractors)")
        loss_df = products_dict["bottom_by_profit"].head(10)
        st.dataframe(
            loss_df.style.format({
                "Sales": "${:,.2f}",
                "Profit": "${:,.2f}",
                "Profit_Margin_Pct": "{:+.2f}%"
            }),
            use_container_width=True
        )


# ----------------------------------------------------
# PAGE 5: CUSTOMER INSIGHTS
# ----------------------------------------------------
elif nav_page == "👥 Customer Insights":
    st.markdown("### 👥 Customer Segments & Client Loyalty")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Unique Customers", f"{customers_dict['total_unique_customers']:,}")
    with c2:
        st.metric("Repeat Customer Rate", f"{customers_dict['repeat_rate_pct']:.2f}%")
    with c3:
        st.metric("Avg Orders Per Customer", f"{customers_dict['avg_orders_per_customer']:.2f}")
        
    st.markdown("---")
    
    r1, r2 = st.columns([1, 1])
    with r1:
        if not customers_dict["segment_breakdown"].empty:
            st.plotly_chart(plot_customer_segment_donut(customers_dict["segment_breakdown"]), use_container_width=True)
        else:
            st.info("Segment column unavailable.")
            
    with r2:
        st.markdown("#### Top 10 Customers by Revenue")
        top_c = customers_dict["top_customers"]
        if not top_c.empty:
            format_dict = {"Sales": "${:,.2f}"}
            if "Profit" in top_c.columns:
                format_dict["Profit"] = "${:,.2f}"
            st.dataframe(top_c.style.format(format_dict), use_container_width=True)
        else:
            st.info("Customer identification columns absent.")


# ----------------------------------------------------
# PAGE 6: BUSINESS INSIGHTS & RECOMMENDATIONS
# ----------------------------------------------------
elif nav_page == "🧠 Business Insights":
    st.markdown("### 🧠 Automated Business Intelligence & Action Plan")
    st.markdown("""
    These findings and recommendations are **dynamically computed** from your active filtered dataset,
    providing verifiable, data-backed guidance for executive decision-makers.
    """)
    
    st.markdown("#### 📌 Measured Key Observations")
    for f in insights_dict["findings"]:
        st.info(f"📊 **Finding:** {f}")
        
    st.markdown("#### 🎯 Strategic Actionable Recommendations")
    for r in insights_dict["recommendations"]:
        st.success(f"✔ **Recommendation:** {r}")


# ----------------------------------------------------
# PAGE 7: DATA QUALITY AUDIT
# ----------------------------------------------------
elif nav_page == "🧹 Data Quality Audit":
    st.markdown("### 🧹 Data Cleaning & Governance Quality Audit")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("Initial Raw Rows", f"{quality_audit['initial_rows']:,}")
    with col_b:
        st.metric("Cleaned Active Rows", f"{quality_audit['final_rows']:,}")
    with col_c:
        st.metric("Duplicates Removed", f"{quality_audit['duplicates_removed']:,}")
    with col_d:
        st.metric("Missing Cells Handled", f"{quality_audit['initial_missing_cells']:,}")
        
    st.markdown("---")
    
    # Missing Values Chart
    missing_dict = val_results["stats"].get("missing_by_column", {})
    if any(v > 0 for v in missing_dict.values()):
        st.plotly_chart(plot_missing_values_bar(missing_dict), use_container_width=True)
    else:
        st.success("✅ Zero missing values detected across initial columns.")
        
    # Statistical Outlier Profiling (IQR)
    st.markdown("#### 📐 Statistical Outlier Detection (IQR Method)")
    st.caption("Outliers are identified using the standard 1.5 × IQR rule. Outliers are flagged for audit without deleting legitimate large enterprise orders.")
    
    outlier_rows = []
    for col_name, info in quality_audit["outlier_audit"].items():
        outlier_rows.append({
            "Column": col_name,
            "Q1 (25th %)": info["q1"],
            "Q3 (75th %)": info["q3"],
            "IQR": info["iqr"],
            "Lower Bound": info["lower_bound"],
            "Upper Bound": info["upper_bound"],
            "Outlier Count": info["outlier_count"],
            "Outlier %": f"{info['outlier_pct']}%"
        })
    if outlier_rows:
        st.dataframe(pd.DataFrame(outlier_rows), use_container_width=True)
        
    # Cleaning Pipeline Audit Trail
    st.markdown("#### 📋 Cleaning Pipeline Operations Log")
    for log_item in quality_audit["audit_log"]:
        st.text(f"• {log_item}")


# ----------------------------------------------------
# PAGE 8: EXPORT & PDF REPORT
# ----------------------------------------------------
elif nav_page == "📥 Export & PDF Report":
    st.markdown("### 📥 Data Export & Executive PDF Reporting")
    st.markdown("Download cleaned data files or generate a comprehensive, executive-ready PDF report.")
    
    c1, c2, c3 = st.columns(3)
    
    # 1. Download Cleaned CSV
    with c1:
        st.markdown("#### 📄 Cleaned CSV")
        csv_buffer = io.StringIO()
        cleaned_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv_buffer.getvalue(),
            file_name="cleaned_sales_data.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    # 2. Download Cleaned Excel
    with c2:
        st.markdown("#### 📊 Cleaned Excel (XLSX)")
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            cleaned_df.to_excel(writer, index=False, sheet_name="CleanedSales")
        st.download_button(
            label="⬇️ Download Cleaned Excel",
            data=excel_buffer.getvalue(),
            file_name="cleaned_sales_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    # 3. Generate Executive PDF Report
    with c3:
        st.markdown("#### 📑 Executive PDF Report")
        try:
            pdf_bytes = generate_pdf_report(
                kpis=kpis,
                insights=insights_dict,
                quality_audit=quality_audit,
                top_products_df=products_dict["top_by_sales"],
                category_df=category_df,
                filter_summary=active_filter_str
            )
            st.download_button(
                label="⬇️ Download Executive PDF",
                data=pdf_bytes,
                file_name="sales_performance_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating PDF report: {e}")

    st.markdown("---")
    st.markdown("#### Preview of Cleaned Dataset (First 50 Rows)")
    st.dataframe(cleaned_df.head(50), use_container_width=True)
