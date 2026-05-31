# E-Commerce Product Price Analyzer

**AI-130 · Programming for Artificial Intelligence · Spring 2026**  
**Group 13 · Abdullah Mughal & Huzaifa Abdur Rahaman**  
**Instructor: Mr. Mustajab Hussain · Air University, Kamra**

---

A web-based analytics dashboard for analyzing Amazon product prices, identifying discount trends, filtering by categories, and visualizing price distributions and outliers.

## Project Features & Pages

| Route | Page | Description |
| :--- | :--- | :--- |
| `/` | **Home Dashboard** | Price distribution histogram, top-8-category boxplot, full category summary table, and a category selection dropdown. |
| `/category` | **Category Analysis** | Detailed category metrics (count, mean price, min/max price, average rating, average discount), category boxplot, and product listings. |
| `/top_deals` | **Top Deals** | Table of the top 20 products sorted by the highest discount percentage. |

---

## Dataset

This project uses the **Amazon Sales Dataset** from Kaggle.
* **Dataset name:** Amazon Sales Dataset
* **Kaggle URL:** [Amazon Sales Dataset on Kaggle](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset)
* **Filename:** `amazon.csv`
* **Storage Location:** Save `amazon.csv` inside the `data/` folder of the project.

---

## Installation & Setup

Follow these steps to set up and run the application locally:

### Step 1: Clone the Repository & Check Python Version
Ensure you have Python 3.10 or higher installed:
```bash
python --version
```

### Step 2: Set Up a Virtual Environment
Navigate to the project root directory and create/activate a virtual environment:

**Linux / macOS:**
```bash
python -m venv E-Commerce
source E-Commerce/bin/activate
```

**Windows:**
```bash
python -m venv E-Commerce
E-Commerce\Scripts\activate
```

### Step 3: Install Required Dependencies
Install the required libraries directly into your active virtual environment:
```bash
pip install flask==3.0.3 pandas==2.2.2 numpy==1.26.4 matplotlib==3.9.0 seaborn==0.13.2
```

### Step 4: Add the Dataset
1. Download the `amazon.csv` file from [Kaggle](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset).
2. Place the downloaded `amazon.csv` file into the `data/` directory at the root of the project.

### Step 5: Run Data Processing & Analysis (Once)
Run the preparation script to clean the data, remove outliers using the IQR method, analyze categories, and generate charts:
```bash
python prepare.py
```
This script processes the raw data and saves the output files (`processed_data.csv`, `category_summary.csv`, `charts.json`, `categories.json`).

### Step 6: Start the Dashboard
Launch the Flask development server:
```bash
python app.py
```
Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## Libraries Used

* **Flask:** Lightweight web framework to build routes, handle requests, and render templates.
* **Pandas:** Used for data cleaning, column type conversions, GroupBy aggregations, and HTML table generation.
* **NumPy:** Used for fast mathematical computations and calculating IQR bounds for price outlier removal.
* **Seaborn & Matplotlib:** Used for generating data visualizations (price histograms and category boxplots) saved as base64-encoded strings for HTML injection.

---

## Troubleshooting & Common Fixes

| Error | Cause | Solution |
| :--- | :--- | :--- |
| `FileNotFoundError: data/amazon.csv` | Missing dataset. | Make sure `amazon.csv` is downloaded from Kaggle and placed in the `data/` folder. |
| `FileNotFoundError: ... not found` | Data is not preprocessed. | Run `python prepare.py` to generate the preprocessed data and charts. |
| `ModuleNotFoundError: No module named 'flask'` | Flask is not installed or venv is inactive. | Run `source E-Commerce/bin/activate` (or equivalent on Windows) and run the install command in Step 3. |
| Browser shows "This site can't be reached" | Flask server is not running. | Run `python app.py` and ensure the terminal process remains open. |
