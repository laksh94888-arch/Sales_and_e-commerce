# Sales & E-Commerce Performance Analytics Dashboard

> **A professional, full-stack Data Analytics Mini Project and interactive Streamlit web application transforming raw sales and transactional data into actionable business intelligence.**

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Problem Statement](#-problem-statement)
3. [Project Objectives](#-project-objectives)
4. [Technologies Used](#-technologies-used)
5. [Dataset Information & Attribution](#-dataset-information--attribution)
6. [College Guidelines Compliance](#-college-guidelines-compliance)
7. [Project Structure](#-project-structure)
8. [Data Cleaning Methodology & Pipeline](#-data-cleaning-methodology--pipeline)
9. [Key Analytical Metrics & Mathematical Formulas](#-key-analytical-metrics--mathematical-formulas)
10. [Dashboard Architecture & Features](#-dashboard-architecture--features)
11. [Installation & Setup Guide](#-installation--setup-guide)
12. [Running the Application](#-running-the-application)
13. [Uploading Custom Datasets (CSV & Excel)](#-uploading-custom-datasets-csv--excel)
14. [Automated Testing Suite](#-automated-testing-suite)
15. [Visual Documentation & Screenshots](#-visual-documentation--screenshots)
16. [Limitations & Edge Cases Handled](#-limitations--edge-cases-handled)
17. [Future Enhancements](#-future-enhancements)
18. [GitHub Upload Instructions](#-github-upload-instructions)

---

## 🔍 Project Overview

The **Sales & E-Commerce Performance Analytics Dashboard** is an enterprise-grade business intelligence platform built using **Python, Pandas, Plotly, Streamlit, and ReportLab**. Designed for business executives, sales operations leads, and data analysts, this application provides an automated, end-to-end analytical workflow:
- Ingests raw sales transaction data in CSV and Excel formats.
- Performs non-destructive data cleaning, type conversion, missing value imputation, and statistical outlier profiling.
- Evaluates operational KPIs (Revenue, Profit, Orders, Quantity, Margin %, and AOV).
- Renders interactive visual dashboards with responsive slice-and-dice filter controls.
- Generates dynamic, data-driven business findings and strategic recommendations calculated on-the-fly.
- Exports cleaned datasets (CSV/XLSX) and compiles executive PDF performance reports.

---

## 🎯 Problem Statement

Modern e-commerce and retail businesses capture millions of transaction lines containing complex relationships between sales channels, discount strategies, delivery tiers, and product categories. However, raw transactional datasets are frequently plagued by missing values, unstandardized column formats, currency symbol pollution, and duplicate records. 

Without robust analytical automation, decision-makers face:
1. **Margin Erosion:** Difficulty identifying heavily discounted transactions that produce negative net profit.
2. **Catalog Underperformance:** Inability to isolate unprofitable merchandise and operational loss leaders.
3. **Geographic Inefficiencies:** Lack of visibility into underperforming sales territories.
4. **Manual Reporting Overhead:** Tedious spreadsheet workflows prone to human calculation errors.

This project delivers a unified, reproducible Python platform that automates ingestion, data hygiene, exploratory analysis, and executive reporting.

---

## 🚀 Project Objectives

1. **Automate Data Hygiene:** Clean, normalize, and validate messy CSV/Excel sales logs without data destruction.
2. **Deliver Real-time KPI Tracking:** Instant calculation of core business health metrics (Gross Sales, Net Profit, Profit Margin %, AOV, and Units Sold).
3. **Analyze Margin Sensitivity:** Empirically evaluate the impact of discount brackets on operating margins.
4. **Perform Multi-Dimensional Segmentation:** Dissect revenue by Geography, Product Category, Sub-Category, and Customer Segments.
5. **Formulate Data-Backed Decisions:** Dynamically compute business findings and actionable recommendations from active filtered data.
6. **Provide Executive Exports:** Enable one-click downloads of cleaned datasets and professional PDF executive reports.

---

## 🛠️ Technologies Used

| Technology | Purpose | Version |
| :--- | :--- | :--- |
| **Python** | Core analytical programming language | `3.10+` (Tested on `3.14`) |
| **Pandas** | High-performance data cleaning, manipulation, and aggregation | `>=2.0.0` |
| **NumPy** | Numerical computations and vector operations | `>=1.24.0` |
| **Streamlit** | Interactive modern web dashboard and user interface | `>=1.30.0` |
| **Plotly Express & Graph Objects** | Interactive, publication-ready visual charts | `>=5.18.0` |
| **OpenPyXL** | Native Microsoft Excel (`.xlsx`) parsing and writing | `>=3.1.0` |
| **ReportLab** | Autonomous generation of executive PDF performance reports | `>=4.0.0` |
| **Pytest** | Automated unit and integration testing suite | `>=7.4.0` |

---

## 📊 Dataset Information & Attribution

The dashboard comes pre-configured with the genuine **Sample Superstore Sales Dataset**, a trusted public benchmark dataset representing an enterprise retail organization across the United States.

- **Primary Source:** [Gist / Tableau Public Superstore Dataset](https://gist.githubusercontent.com/nnbphuong/38db511db14542f3ba9ef16e69d3814c/raw/3a77ff9d97c504d3ec3210b12fde7242b8c6ab63/Superstore.csv)
- **Reference Repository:** [Kaggle Superstore Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
- **Format:** CSV (`data/sample_sales_data.csv`) and XLSX sample (`data/sample_sales_data.xlsx`).
- **Records:** **9,994 rows**
- **Attributes:** **21 columns** (Order ID, Order Date, Ship Date, Ship Mode, Customer ID, Customer Name, Segment, Country, City, State, Postal Code, Region, Product ID, Category, Sub-Category, Product Name, Sales, Quantity, Discount, Profit).
- **License:** Public Domain / Educational Dataset.

---

## 🎓 College Guidelines Compliance

| Guideline Requirement | Minimum Required | Project Implementation | Compliance Status |
| :--- | :--- | :--- | :--- |
| **Record Count** | Minimum 500 rows | **9,994 rows** | ✅ Exceeded |
| **Feature Count** | Minimum 10 columns | **21 features** | ✅ Exceeded |
| **Data Nature** | Numerical & Categorical | 4 Numerical, 15 Categorical, 2 DateTime | ✅ Met |
| **Dataset Source** | Reliable & Documented | Public Tableau benchmark with URL | ✅ Met |
| **Data Cleaning** | Cleaning & Transformation | Reusable pipeline in `src/data_cleaning.py` | ✅ Met |
| **Interactive Dashboard** | Meaningful insights | 8-section interactive Streamlit app | ✅ Met |
| **Automated Testing** | Reliability validation | 18 automated tests passing in Pytest | ✅ Met |

---

## 📁 Project Structure

```text
sales-ecommerce-analytics/
│
├── app.py                      # Main Streamlit web application & UI
├── requirements.txt            # Locked project dependencies
├── README.md                   # Full college documentation & user manual
├── .gitignore                  # Git exclusions for cache, venv, and temporary files
│
├── data/
│   ├── sample_sales_data.csv   # Genuine Superstore sales dataset (9,994 rows)
│   ├── sample_sales_data.xlsx  # Excel sample dataset for upload testing
│   └── README.md               # Dataset documentation & column dictionary
│
├── src/
│   ├── __init__.py             # Package marker
│   ├── data_loader.py          # CSV/Excel ingestion, column mapping, validation
│   ├── data_cleaning.py        # Cleaning pipeline, imputation, IQR outlier detection
│   ├── analysis.py             # KPIs, aggregations, customer metrics, dynamic insights
│   ├── visualizations.py       # Plotly chart generation with executive styling
│   └── report_generator.py     # PDF generation engine using ReportLab
│
├── tests/
│   ├── __init__.py             # Test package marker
│   ├── test_data_cleaning.py   # Unit tests for duplicates, nulls, dates, numbers
│   ├── test_analysis.py        # Unit tests for KPI formulas and insights
│   └── test_validation.py      # Unit tests for schema and minimum bounds
│
├── reports/
│   └── README.md               # Documentation of generated PDF reports
│
└── screenshots/
    └── README.md               # Visual dashboard gallery
```

---

## 🧹 Data Cleaning Methodology & Pipeline

The preprocessing pipeline in `src/data_cleaning.py` executes an 8-step hygiene routine that never modifies the original dataset:

1. **Non-Destructive Copying:** Deep-copies the raw DataFrame into working memory.
2. **Column Standardization:** Strips whitespace and maps common variations (e.g. `order_date`, `revenue`, `qty`, `net_profit`) to canonical analytical columns using a dictionary synonym mapper.
3. **Duplicate Record Detection & Removal:** Identifies exact row duplicates and removes them while tracking the exact count removed.
4. **Text Normalization:** Strips trailing/leading spaces on all text features and converts empty string representations (`"nan"`, `"None"`, `"null"`) to true `NaN`.
5. **Numeric Sanitization:** Strips currency symbols (`$`), commas (`,`), and percentage symbols (`%`), and translates accounting parenthetical negatives (e.g. `"(120.50)"` $\rightarrow$ `-120.50`).
6. **Temporal Standardization:** Robustly parses date strings into `datetime64[ns]` formats.
7. **Missing Value Imputation:**
   - Numerical (`Sales`, `Profit`): Imputed with distribution **median** (or dropped if configured).
   - Incentive (`Discount`): Imputed with `0.0` (zero discount baseline).
   - Categorical (`Category`, `Region`, `Segment`, `State`): Imputed with `"Unknown"`.
8. **Statistical Outlier Profiling (IQR):** Calculates the Interquartile Range ($IQR = Q_3 - Q_1$) and establishes upper/lower thresholds ($[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$). Outlier rows are quantified and audited without blindly deleting legitimate high-volume enterprise orders.

---

## 📐 Key Analytical Metrics & Mathematical Formulas

The dashboard calculates standardized corporate metrics:

1. **Total Sales ($):**
   $$\text{Total Sales} = \sum_{i=1}^{n} \text{Sales}_i$$

2. **Total Profit ($):**
   $$\text{Total Profit} = \sum_{i=1}^{n} \text{Profit}_i$$

3. **Overall Profit Margin (%):**
   $$\text{Profit Margin} = \left( \frac{\text{Total Profit}}{\text{Total Sales}} \right) \times 100$$
   *(Guarded against division by zero: if Sales = $0, Margin = 0.0%)*

4. **Total Orders:**
   $$\text{Total Orders} = \text{Count of Unique}(\text{Order ID})$$

5. **Average Order Value (AOV):**
   $$\text{AOV} = \frac{\text{Total Sales}}{\text{Total Orders}}$$

6. **Month-over-Month (MoM) Growth (%):**
   $$\text{MoM Growth}_t = \left( \frac{\text{Sales}_t - \text{Sales}_{t-1}}{\text{Sales}_{t-1}} \right) \times 100$$

7. **Repeat Customer Rate (%):**
   $$\text{Repeat Rate} = \left( \frac{\text{Customers with } > 1 \text{ Order}}{\text{Total Unique Customers}} \right) \times 100$$

---

## 🖥️ Dashboard Architecture & Features

The Streamlit dashboard (`app.py`) is organized into 8 modular sections accessible via the sidebar navigation:

1. **📊 Executive Overview:**
   - Six top KPI cards (Total Sales, Net Profit, Profit Margin %, Total Orders, Units Sold, and Average Order Value).
   - High-level monthly sales trend and category comparisons.
   - Expandable metric glossary.

2. **📈 Sales & Trends:**
   - Temporal monthly trend line with interactive hover details.
   - Tabular summary of monthly sales, profits, and MoM growth rates.
   - Geographic distribution across sales territories and top 10 states.

3. **💰 Profitability & Discounts:**
   - Sub-category net profit vs. loss breakdown (emerald green for profitable items, crimson red for loss makers).
   - Discount tier margin analysis demonstrating margin erosion across discount brackets ($0\%$, $1\text{--}10\%$, $11\text{--}20\%$, $21\text{--}30\%$, $>30\%$).

4. **📦 Product Analytics:**
   - Top 10 products ranked by gross revenue.
   - Top 10 products ranked by net profit.
   - Catalog detractor table highlighting the biggest loss-making SKUs.

5. **👥 Customer Insights:**
   - Customer loyalty scorecard (Total Unique Clients, Repeat Customer Rate %, Average Orders per Client).
   - Donut chart depicting sales distribution across customer segments (`Consumer`, `Corporate`, `Home Office`).
   - Top 10 client accounts by revenue.

6. **🧠 Business Insights:**
   - **Measured Key Observations:** Automatically generated findings reflecting active filtered data (top region contribution, category leaders, seasonality peaks).
   - **Strategic Recommendations:** Tailored operational directives (discount caps, inventory lead times, marketing focus).

7. **🧹 Data Quality Audit:**
   - Before-and-after audit scorecard (initial rows vs. cleaned active rows).
   - Duplicate records eliminated and missing cells handled.
   - Missing values distribution bar chart.
   - Statistical IQR outlier boundaries and percentages.
   - Chronological pipeline audit log.

8. **📥 Export & PDF Report:**
   - Download cleaned dataset as **CSV**.
   - Download cleaned dataset as **Excel (.xlsx)**.
   - Generate and download an **Executive PDF Report** compiling KPIs, insights, top products, and data quality metrics.
   - Live interactive 50-row preview of cleaned data.

---

## 💻 Installation & Setup Guide

### Prerequisites
- Python `3.10` or higher installed on your system.
- Git installed on your system.

### Step 1: Clone or Open the Workspace
```bash
git clone https://github.com/<your-username>/sales-ecommerce-analytics-dashboard.git
cd sales-ecommerce-analytics-dashboard
```

### Step 2: Create and Activate a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv venv
.\venv\Scripts\activate.bat

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

Launch the Streamlit web application with:

```bash
streamlit run app.py
```

The application will start and automatically open in your default browser at:
```text
http://localhost:8501
```

---

## 📂 Uploading Custom Datasets (CSV & Excel)

The dashboard is designed to analyze both the bundled Superstore data and external client files:

1. In the sidebar, select **"Upload Custom File (CSV/XLSX)"**.
2. Click **Browse files** and upload your `.csv`, `.xlsx`, or `.xls` file.
3. The validation engine will:
   - Check minimum row count (warnings if $<500$ rows).
   - Check minimum column count (warnings if $<10$ columns).
   - Automatically standardize common column aliases (e.g. `revenue` $\rightarrow$ `Sales`, `order_date` $\rightarrow$ `Order Date`).
   - Gracefully disable optional charts if specific dimensions (like `Region` or `Discount`) are missing without crashing.

---

## 🧪 Automated Testing Suite

The repository contains an automated test suite executed with `pytest` covering:
- Duplicate detection and removal.
- Missing value imputation and text sanitization.
- Date and numeric type conversions.
- IQR outlier detection boundaries.
- KPI mathematical correctness and zero-division edge cases.
- MoM monthly growth calculation.
- Dynamic business insight formulation.
- Schema bounds and required column validation.

### Run All Tests:
```bash
pytest -v
```

### Test Output Verification:
```text
tests/test_analysis.py::test_calculate_kpis_correctness PASSED
tests/test_analysis.py::test_calculate_kpis_zero_sales PASSED
tests/test_analysis.py::test_monthly_trends PASSED
tests/test_analysis.py::test_discount_impact_analysis PASSED
tests/test_analysis.py::test_product_rankings PASSED
tests/test_analysis.py::test_customer_repeat_rate PASSED
tests/test_analysis.py::test_dynamic_business_insights PASSED
tests/test_data_cleaning.py::test_clean_numeric_series PASSED
tests/test_data_cleaning.py::test_duplicate_removal PASSED
tests/test_data_cleaning.py::test_missing_values_imputation PASSED
tests/test_data_cleaning.py::test_date_conversion PASSED
tests/test_data_cleaning.py::test_whitespace_stripping PASSED
tests/test_data_cleaning.py::test_outlier_detection_iqr PASSED
tests/test_validation.py::test_empty_dataframe_validation PASSED
tests/test_validation.py::test_minimum_rows_and_columns_check PASSED
tests/test_validation.py::test_college_guidelines_warnings PASSED
tests/test_validation.py::test_missing_sales_column_error PASSED
tests/test_validation.py::test_column_standardization_aliases PASSED

============================= 18 passed in 0.46s =============================
```

---

## 📸 Visual Documentation & Screenshots

| View | Description |
| :--- | :--- |
| **01. Executive Overview** | High-level KPI Scorecard and primary sales trend charts. |
| **02. Sales & Trends** | Monthly time-series performance and geographic breakdown. |
| **03. Profitability** | Sub-category profit/loss and discount bracket margin erosion. |
| **04. Product Performance** | Top 10 products by revenue and catalog loss leaders. |
| **05. Customer Analytics** | Segment distribution and repeat customer loyalty metrics. |
| **06. Business Insights** | Measured analytical findings and data-driven recommendations. |
| **07. Data Quality Audit** | Data cleaning statistics, missing values, and IQR outlier analysis. |
| **08. Data Export & PDF** | Cleaned CSV/XLSX download and executive PDF report generator. |

*(Full-resolution screenshots are located in the `screenshots/` directory).*

---

## ⚠️ Limitations & Edge Cases Handled

1. **Non-Destructive Outlier Handling:** Statistical outliers identified via IQR are audited and flagged, but not automatically deleted, preventing the loss of legitimate enterprise wholesale transactions.
2. **Missing Feature Graceful Fallback:** If an uploaded dataset lacks optional dimensions (e.g., `Discount` or `Ship Mode`), dependent charts are cleanly hidden or replaced with informational banners rather than raising runtime errors.
3. **Zero Sales Division Guard:** All profit margin and growth formulas contain mathematical zero-checks to avoid `ZeroDivisionError`.
4. **Encoding Resilience:** The CSV loader automatically tries `utf-8`, `latin1`, and `cp1252` encodings to handle diverse legacy files.

---

## 🔮 Future Enhancements

1. **Machine Learning Forecasting:** Integrate an ARIMA / Prophet time-series model to forecast sales 6 months into the future.
2. **Customer Lifetime Value (CLV):** Implement RFM (Recency, Frequency, Monetary) segmentation.
3. **Database Integration:** Connect to PostgreSQL, Snowflake, or BigQuery for direct data ingestion.
4. **Automated Email Reports:** Schedule recurring weekly PDF executive summaries via SMTP.

---

## 📤 GitHub Upload Instructions

Follow these exact steps to push this project to your GitHub account:

### 1. Initialize Git in the Project Directory
Open your terminal in the project directory (`sales-ecommerce-analytics`) and run:
```bash
git init
```

### 2. Configure Git User Identity (If not already configured)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Stage All Project Files
```bash
git add .
```

### 4. Create Initial Commit
```bash
git commit -m "feat: complete sales and ecommerce performance analytics dashboard"
```

### 5. Create a New Repository on GitHub
1. Go to [GitHub](https://github.com/) and log in.
2. Click **New Repository** (or visit `https://github.com/new`).
3. Set Repository Name: `sales-ecommerce-analytics-dashboard`
4. Choose **Public**.
5. Do **NOT** check "Add a README", "Add .gitignore", or "Add a license" (we already created them locally).
6. Click **Create repository**.

### 6. Link Remote and Push
Copy your repository URL from GitHub and run:
```bash
git branch -M main
git remote add origin https://github.com/<your-username>/sales-ecommerce-analytics-dashboard.git
git push -u origin main
```

---

## 👨‍💻 Project Evaluation Summary
- **Title:** Sales & E-Commerce Performance Analytics Dashboard
- **Subject:** Data Analytics / Business Intelligence Mini Project
- **Domain:** E-Commerce, Retail Sales, Enterprise Business Intelligence
- **Status:** Complete, Fully Tested, and Production-Ready.
