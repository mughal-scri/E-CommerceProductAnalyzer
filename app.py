"""
app.py
------
Flask web application for P-13: E-Commerce Product Price Analyzer.

Routes
------
GET  /            → Home: price histplot + overall category summary table + category dropdown
POST /category    → Filtered view: summary stats + boxplot for selected category
GET  /top_deals   → Top 20 products by highest discount percentage (HTML table)
"""

import json
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

from analysis import (
    get_category_filtered,
    get_single_category_boxplot,
    get_top_deals,
)

app = Flask(__name__)


# ── Load all artifacts once at startup ──────────────────────────────────────
try:
    DF = pd.read_csv('data/processed_data.csv')
    SUMMARY = pd.read_csv('data/category_summary.csv')

    with open('charts.json', 'r') as f:
        CHARTS = json.load(f)

    with open('categories.json', 'r') as f:
        CATEGORIES = json.load(f)

    print(f"[app] Dataset loaded: {len(DF)} products, {len(CATEGORIES)} categories.")
    print("[app] Flask is ready.")

except FileNotFoundError as e:
    print(f"[app] ERROR: {e}")
    print("[app] Please run 'python prepare.py' first.")
    DF, SUMMARY, CHARTS, CATEGORIES = None, None, {}, []


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def index():
    """
    Home page — shows:
      - Overall discounted price histogram (Seaborn histplot)
      - Overall category summary table (GroupBy result)
      - Dropdown to explore a specific category
    """
    summary_html = SUMMARY.to_html(
        classes='summary-table',
        index=False,
        border=0,
    )

    return render_template(
        'index.html',
        histplot=CHARTS.get('histplot', ''),
        boxplot=CHARTS.get('boxplot', ''),
        summary_table=summary_html,
        categories=CATEGORIES,
        total_products=len(DF),
        total_categories=len(CATEGORIES),
    )


@app.route('/category', methods=['POST'])
def category():
    """
    Filtered category page — shows:
      - Summary stats for the selected category
      - Seaborn boxplot for that category
      - Filtered product table (up to 30 rows)
    """
    selected = request.form.get('category', '').strip()

    if not selected:
        return redirect(url_for('index'))

    try:
        filtered_df = get_category_filtered(DF, selected)
        boxplot_b64 = get_single_category_boxplot(DF, selected)

        # Stats for display
        stats = {
            'count':        len(filtered_df),
            'mean_price':   round(filtered_df['discounted_price'].mean(), 2),
            'min_price':    round(filtered_df['discounted_price'].min(), 2),
            'max_price':    round(filtered_df['discounted_price'].max(), 2),
            'mean_rating':  round(filtered_df['rating'].mean(), 2),
            'mean_discount':round(filtered_df['discount_percentage'].mean(), 2),
        }

        # Table — show top 30 only to keep page readable
        table_html = (
            filtered_df[['product_name', 'actual_price', 'discounted_price', 'discount_percentage', 'rating']]
            .head(30)
            .to_html(classes='summary-table', index=False, border=0)
        )

        return render_template(
            'category.html',
            selected=selected,
            stats=stats,
            boxplot=boxplot_b64,
            table=table_html,
            categories=CATEGORIES,
        )

    except ValueError as e:
        return render_template(
            'index.html',
            histplot=CHARTS.get('histplot', ''),
            boxplot=CHARTS.get('boxplot', ''),
            summary_table=SUMMARY.to_html(classes='summary-table', index=False, border=0),
            categories=CATEGORIES,
            total_products=len(DF),
            total_categories=len(CATEGORIES),
            error=str(e),
        )
    except Exception as e:
        return render_template(
            'index.html',
            histplot=CHARTS.get('histplot', ''),
            boxplot=CHARTS.get('boxplot', ''),
            summary_table=SUMMARY.to_html(classes='summary-table', index=False, border=0),
            categories=CATEGORIES,
            total_products=len(DF),
            total_categories=len(CATEGORIES),
            error=f"Unexpected error: {str(e)}",
        )


@app.route('/top_deals', methods=['GET'])
def top_deals():
    """
    Top Deals page — shows the 20 products with the
    highest discount percentage as an HTML table.
    """
    top = get_top_deals(DF, n=20)

    table_html = top.to_html(
        classes='summary-table',
        index=True,
        border=0,
    )

    return render_template(
        'top_deals.html',
        table=table_html,
        categories=CATEGORIES,
    )


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
