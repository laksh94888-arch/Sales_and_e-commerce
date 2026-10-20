"""
Executive PDF Report Generator
Generates a downloadable, high-quality business analytics PDF report using ReportLab.
Includes executive KPI tables, calculated data-driven insights, product rankings,
and data quality governance summaries.
"""

import io
from datetime import datetime
from typing import Dict, Any
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_pdf_report(
    kpis: Dict[str, Any],
    insights: Dict[str, Any],
    quality_audit: Dict[str, Any],
    top_products_df: pd.DataFrame,
    category_df: pd.DataFrame,
    filter_summary: str = "All records"
) -> bytes:
    """
    Compiles an executive PDF report and returns the PDF bytes buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#312E81")    # Deep Indigo
    c_secondary = colors.HexColor("#4F46E5")  # Indigo
    c_dark = colors.HexColor("#1E293B")       # Dark Slate
    c_light = colors.HexColor("#F8FAFC")      # Soft Gray
    c_accent = colors.HexColor("#10B981")     # Emerald
    c_border = colors.HexColor("#E2E8F0")     # Light Border
    
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_primary,
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=c_dark
    )
    
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=c_secondary,
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=c_dark
    )
    
    bullet_style = ParagraphStyle(
        "DocBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_dark,
        leftIndent=15
    )
    
    story = []
    
    # 1. Header Banner
    story.append(Paragraph("SALES & E-COMMERCE PERFORMANCE REPORT", title_style))
    story.append(Spacer(1, 4))
    gen_time = datetime.now().strftime("%B %d, %Y - %H:%M")
    story.append(Paragraph(f"<b>Generated:</b> {gen_time} &nbsp;|&nbsp; <b>Scope:</b> {filter_summary}", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceAfter=12))
    
    # 2. Executive KPI Summary Table
    story.append(Paragraph("1. Executive KPI Summary", section_heading))
    kpi_data = [
        ["Total Revenue", f"${kpis.get('total_sales', 0):,.2f}", "Total Orders", f"{kpis.get('total_orders', 0):,}"],
        ["Net Profit", f"${kpis.get('total_profit', 0):,.2f}", "Total Quantity Sold", f"{kpis.get('total_quantity', 0):,}"],
        ["Profit Margin", f"{kpis.get('profit_margin_pct', 0):.2f}%", "Avg Order Value (AOV)", f"${kpis.get('avg_order_value', 0):,.2f}"],
        ["Avg Discount", f"{kpis.get('avg_discount_pct', 0):.2f}%", "Audited Records", f"{quality_audit.get('final_rows', 0):,}"]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[130, 140, 130, 140])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), c_light),
        ("BACKGROUND", (2, 0), (2, -1), c_light),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, -1), c_dark),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
        ("BOX", (0, 0), (-1, -1), 1, c_secondary),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))
    
    # 3. Automated Business Insights
    story.append(Paragraph("2. Measured Business Insights", section_heading))
    findings = insights.get("findings", [])
    if findings:
        for f in findings:
            story.append(Paragraph(f"• {f}", bullet_style))
            story.append(Spacer(1, 3))
    else:
        story.append(Paragraph("No critical findings generated for current filter selection.", body_style))
        
    story.append(Spacer(1, 8))
    
    # 4. Strategic Recommendations
    story.append(Paragraph("3. Strategic Action Plan & Recommendations", section_heading))
    recs = insights.get("recommendations", [])
    if recs:
        for r in recs:
            story.append(Paragraph(f"✔ <b>Action:</b> {r}", bullet_style))
            story.append(Spacer(1, 3))
    else:
        story.append(Paragraph("Maintain active operational controls and monitor weekly performance metrics.", body_style))
        
    story.append(Spacer(1, 10))
    
    # 5. Category Performance Summary Table
    if not category_df.empty:
        story.append(Paragraph("4. Category Performance Overview", section_heading))
        cat_rows = [["Category", "Sales ($)", "Profit ($)", "Margin (%)"]]
        for _, row in category_df.head(5).iterrows():
            cat_rows.append([
                str(row.get("Category", "N/A")),
                f"${row.get('Sales', 0):,.2f}",
                f"${row.get('Profit', 0):,.2f}",
                f"{row.get('Profit_Margin_Pct', 0):.2f}%"
            ])
        cat_table = Table(cat_rows, colWidths=[180, 120, 120, 120])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_secondary),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("BOX", (0, 0), (-1, -1), 1, c_secondary),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_light]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 10))
        
    # 6. Top 5 Products Table
    if not top_products_df.empty:
        story.append(Paragraph("5. Top Revenue Generating Products", section_heading))
        prod_rows = [["Product Name", "Sales ($)", "Profit ($)"]]
        prod_col = "Product Name" if "Product Name" in top_products_df.columns else "Product ID"
        for _, row in top_products_df.head(5).iterrows():
            name = str(row.get(prod_col, "N/A"))
            clean_name = (name[:45] + "...") if len(name) > 45 else name
            prod_rows.append([
                clean_name,
                f"${row.get('Sales', 0):,.2f}",
                f"${row.get('Profit', 0):,.2f}"
            ])
        prod_table = Table(prod_rows, colWidths=[280, 130, 130])
        prod_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_primary),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("BOX", (0, 0), (-1, -1), 1, c_primary),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_light]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(prod_table)
        story.append(Spacer(1, 10))
        
    # 7. Data Quality Audit Summary
    story.append(Paragraph("6. Data Quality & Cleaning Audit", section_heading))
    dq_text = (
        f"Initial Dataset Records: <b>{quality_audit.get('initial_rows', 0):,}</b> | "
        f"Final Cleaned Records: <b>{quality_audit.get('final_rows', 0):,}</b> | "
        f"Duplicates Eliminated: <b>{quality_audit.get('duplicates_removed', 0):,}</b> | "
        f"Missing Values Imputed: <b>{quality_audit.get('initial_missing_cells', 0):,}</b>"
    )
    story.append(Paragraph(dq_text, body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_border, spaceAfter=8))
    story.append(Paragraph("<i>Report generated autonomously by Sales & E-Commerce Performance Analytics System.</i>", ParagraphStyle(
        "Footer", parent=styles["Italic"], fontSize=8, textColor=colors.gray, alignment=1
    )))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
