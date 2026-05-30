"""
analysis.py
-----------
GroupBy aggregation and chart generation for P-13.
All charts are returned as base64-encoded PNG strings
so Flask can embed them directly in HTML templates.
"""

import io
import base64

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')          # non-interactive backend — required for Flask
import matplotlib.pyplot as plt
import seaborn as sns


# ── GroupBy summary ──────────────────────────────────────────────────────────

def get_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use GroupBy to compute per-category statistics:
      - mean discounted price
      - mean rating
      - product count

    Sorted by mean discounted price descending.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame (after outlier removal).

    Returns
    -------
    pd.DataFrame
        Summary table with one row per category.
    """
    summary = (
        df.groupby('category')
        .agg(
            mean_price   = ('discounted_price', 'mean'),
            mean_rating  = ('rating',           'mean'),
            product_count= ('product_name',     'count'),
        )
        .reset_index()
        .sort_values('mean_price', ascending=False)
    )

    summary['mean_price']  = summary['mean_price'].round(2)
    summary['mean_rating'] = summary['mean_rating'].round(2)

    print(f"[analysis] Category summary: {len(summary)} categories.")
    return summary


def get_category_filtered(df: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    Filter the DataFrame to a single category and return it
    sorted by discount_percentage descending.

    Parameters
    ----------
    df : pd.DataFrame
        Full cleaned DataFrame.
    category : str
        Category name to filter on.

    Returns
    -------
    pd.DataFrame
        Filtered and sorted DataFrame.

    Raises
    ------
    ValueError
        If the category is not found in the dataset.
    """
    filtered = df[df['category'] == category].copy()

    if filtered.empty:
        raise ValueError(f"Category '{category}' not found in dataset.")

    filtered = filtered.sort_values('discount_percentage', ascending=False)
    print(f"[analysis] Filtered '{category}': {len(filtered)} products.")
    return filtered


def get_top_deals(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """
    Return the top N products with the highest discount percentage.

    Parameters
    ----------
    df : pd.DataFrame
        Full cleaned DataFrame.
    n : int
        Number of top deals to return (default 20).

    Returns
    -------
    pd.DataFrame
        Top N rows sorted by discount_percentage descending.
    """
    top = (
        df[['product_name', 'category', 'actual_price', 'discounted_price', 'discount_percentage', 'rating']]
        .dropna(subset=['discount_percentage'])
        .sort_values('discount_percentage', ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    top.index += 1    # start rank from 1
    return top


# ── Chart generators ─────────────────────────────────────────────────────────

def get_price_histplot(df: pd.DataFrame) -> str:
    """
    Create a Seaborn histplot of overall discounted prices.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame (after outlier removal).

    Returns
    -------
    str
        Base64-encoded PNG string for use in an HTML <img> tag.
    """
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.histplot(df['discounted_price'].dropna(), bins=40, kde=True,
                 color='#2E75B6', ax=ax)
    ax.set_xlabel('Discounted Price (₹)', fontsize=11)
    ax.set_ylabel('Number of Products', fontsize=11)
    ax.set_title('Distribution of Discounted Prices (after outlier removal)', fontsize=13, fontweight='bold')
    plt.tight_layout()

    result = _fig_to_base64(fig)
    plt.close(fig)
    return result


def get_category_boxplot(df: pd.DataFrame, top_n: int = 8) -> str:
    """
    Create a Seaborn box plot of discounted prices for the top N categories
    (by product count).

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame (after outlier removal).
    top_n : int
        How many categories to include (default 8).

    Returns
    -------
    str
        Base64-encoded PNG string.
    """
    # Pick top N categories by product count
    top_cats = (
        df['category'].value_counts()
        .head(top_n)
        .index.tolist()
    )
    df_top = df[df['category'].isin(top_cats)]

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.boxplot(
        data=df_top,
        x='category',
        y='discounted_price',
        hue='category',
        palette='Set2',
        legend=False,
        ax=ax,
    )
    ax.set_xlabel('Category', fontsize=11)
    ax.set_ylabel('Discounted Price (₹)', fontsize=11)
    ax.set_title(f'Price Distribution — Top {top_n} Categories', fontsize=13, fontweight='bold')
    plt.xticks(rotation=30, ha='right', fontsize=9)
    plt.tight_layout()

    result = _fig_to_base64(fig)
    plt.close(fig)
    return result


def get_single_category_boxplot(df: pd.DataFrame, category: str) -> str:
    """
    Create a Seaborn box plot for a single selected category.

    Parameters
    ----------
    df : pd.DataFrame
        Full cleaned DataFrame.
    category : str
        Category name to visualize.

    Returns
    -------
    str
        Base64-encoded PNG string.
    """
    filtered = df[df['category'] == category]

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(y=filtered['discounted_price'], color='#2E75B6', ax=ax)
    ax.set_ylabel('Discounted Price (₹)', fontsize=11)
    ax.set_title(f'Price Distribution — {category}', fontsize=12, fontweight='bold')
    plt.tight_layout()

    result = _fig_to_base64(fig)
    plt.close(fig)
    return result


# ── Internal helper ──────────────────────────────────────────────────────────

def _fig_to_base64(fig) -> str:
    """Convert a Matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return encoded
