"""
prepare.py
----------
Run this script ONCE before starting the Flask app.
It loads, cleans, and processes the dataset, then saves:
  - processed_data.csv  (cleaned DataFrame)
  - charts.json         (base64-encoded chart strings)

Usage
-----
    python prepare.py
"""

import json
import pandas as pd

from data_processing import load_data, clean_data, add_discount_amount, remove_outliers
from analysis import (
    get_category_summary,
    get_price_histplot,
    get_category_boxplot,
)


def main():
    """Full data preparation pipeline — run once before starting Flask."""

    # ── Step 1: Load ─────────────────────────────────────────────────────────
    df = load_data('data/amazon.csv')

    # ── Step 2: Clean ────────────────────────────────────────────────────────
    df = clean_data(df)

    # ── Step 3: Feature engineering — discount_amount ─────────────────────────
    df = add_discount_amount(df)

    # ── Step 4: Remove outliers using IQR ────────────────────────────────────
    df = remove_outliers(df, col='discounted_price')

    # ── Step 5: Save cleaned data to CSV ─────────────────────────────────────
    df.to_csv('data/processed_data.csv', index=False)
    print("[prepare] processed_data.csv saved.")

    # ── Step 6: Compute and save category summary ─────────────────────────────
    summary = get_category_summary(df)
    summary.to_csv('data/category_summary.csv', index=False)
    print("[prepare] category_summary.csv saved.")

    # ── Step 7: Generate and save charts ─────────────────────────────────────
    print("[prepare] Generating charts (this may take a few seconds)...")
    histplot_b64 = get_price_histplot(df)
    boxplot_b64  = get_category_boxplot(df, top_n=8)

    with open('charts.json', 'w') as f:
        json.dump({
            'histplot': histplot_b64,
            'boxplot':  boxplot_b64,
        }, f)
    print("[prepare] charts.json saved.")

    # ── Step 8: Save category list for Flask dropdown ─────────────────────────
    categories = sorted(df['category'].dropna().unique().tolist())
    with open('categories.json', 'w') as f:
        json.dump(categories, f)
    print(f"[prepare] categories.json saved — {len(categories)} categories.")

    print("\n[prepare] ✓ All done! Now run:  python app.py")


if __name__ == '__main__':
    main()
