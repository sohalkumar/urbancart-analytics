# UrbanCart E-Commerce Analytics

An end-to-end data analytics project: raw messy data → SQL analysis →
Python EDA → a 5-page Tableau dashboard covering revenue, profitability,
marketing performance, customers, and operations for a fictional Indian
D2C retail brand ("UrbanCart").

🔗 **Live Dashboard:** [add your Tableau Public link here]

> **Note on the data:** No live e-commerce dataset was available for this
> project, so the underlying data is synthetically generated
> (`generate_data.py`) to realistically mimic an Indian D2C brand's order
> history — including seasonality, regional distribution, marketing spend,
> and intentionally messy raw data (duplicates, nulls, inconsistent date
> formats, channel-name mismatches) to clean. The analysis techniques,
> SQL, and dashboard are all real work.

## Dashboard pages

1. **Executive Overview** — revenue/profit trends, category revenue mix, KPI cards
2. **Profitability** — profit and margin % by category, top profit products
3. **Marketing Performance** — ROAS and CAC by channel, spend vs. revenue trend
4. **Customers** — RFM segmentation, LTV by acquisition channel, revenue by city
5. **Operations** — payment method mix, cancellation/return rate by category

## Tech stack

- **Python** (pandas, numpy) — data generation & cleaning pipeline
- **SQL** (SQLite) — 12 business-question queries: CTEs, window functions, LOD-style aggregation
- **Tableau** — 5-page interactive dashboard, including relationship modeling and LOD expressions
- **Matplotlib** — exploratory charts

## Project structure

```
urbancart-analytics/
├── generate_data.py          # creates the raw (intentionally messy) dataset
├── clean_data.py              # cleaning pipeline -> data_clean/
├── sql_analysis.sql           # 12 business-question SQL queries
├── DASHBOARD_REQUIREMENTS.md  # the dashboard brief this project was built against
├── data_raw/                  # raw CSVs with data quality issues
├── data_clean/                 # cleaned CSVs
├── analytics.twbx              # packaged Tableau workbook
└── README.md
```

## Key findings

- Festive-season (Oct-Nov) revenue runs roughly 2-2.5x baseline months
- Beauty & Personal Care has the lowest revenue but the **highest profit
  margin** of any category — profit and revenue tell different stories
- Influencer marketing is simultaneously the **worst ROAS and worst CAC**
  of any paid channel — a clear "cut this spend" signal
- Organic Search delivers the highest average customer LTV, at zero
  acquisition cost

## How to run this yourself

```bash
python3 generate_data.py     # generates data_raw/
python3 clean_data.py        # produces data_clean/
sqlite3 data_clean/urbancart.db < sql_analysis.sql   # run all SQL queries
```

Open `analytics.twbx` in Tableau to explore the dashboard, or view the
published version at the live link above.