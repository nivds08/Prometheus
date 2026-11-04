# Customer Analytics & Churn Prediction

This project helps an online store answer a simple question:

**Who are our customers, who is about to stop buying, and what should we do about it?**

It takes order and customer data, studies buying habits, groups similar shoppers, flags people who look likely to leave, and shows all of that in a local web dashboard.

---

## What you can see

Open the dashboard and you get six pages:

1. **Summary** — the big numbers (sales, orders, customers) plus a short written briefing you can download as a report.
2. **Business** — how sales and orders change over time, and which product categories make money or get returned a lot.
3. **Retention** — of the people who first bought in a given month, how many came back later.
4. **Segments** — customers grouped by how recently they bought, how often they buy, and how much they spend (for example Champions vs inactive shoppers).
5. **Churn risk** — a score for each customer: Low, Medium, or High chance they have already gone quiet. You can search the high-risk list and export it.
6. **Map** — where customers and revenue sit by country and U.S. state.

The left panel lets you filter by country, traffic source, segment, and risk level. You can collapse that panel when you want more space.

---

## How it works (in plain terms)

1. Customer and order files are loaded into a local database.
2. SQL answers the business questions: monthly sales, repeat-buy rates, profit by category, and a score for each shopper.
3. A clustering model puts shoppers into named groups.
4. A prediction model estimates who has gone quiet (no order in 90 days) and why, without cheating by using “days since last order” as an input.
5. Streamlit draws the charts and the written insights.

Everything runs on your computer. You do not need a cloud account.

---

## Run it

You need Python 3 on your machine.

```bash
python -m pip install -r requirements.txt
python run_pipeline.py
streamlit run dashboard/app.py
```

The first command installs the libraries.  
The second builds the database and trains the models. If you do not already have raw CSV files in `ecommerce/`, it creates a demo dataset so you can still try the app.  
The third command opens the dashboard in your browser (usually `http://localhost:8501`).

Do **not** run `streamlit run run_pipeline.py`. That file is the data build step, not the website.

---

## Project folders

| Folder | What it is for |
|---|---|
| `ecommerce/` | Raw customer and order CSVs |
| `db/` | Local database created by the pipeline |
| `sql/` | The business questions written as SQL |
| `ml/` | Customer grouping and churn scoring |
| `dashboard/` | The website you look at |
| `scripts/` | Load data, run SQL, and helper tools |
| `run_pipeline.py` | One command that does the full build |

---

## Data note

This is ecommerce-style data (customers, orders, products, returns). On a full dataset you would see around 100,000 customers. The demo dataset is smaller, so the charts look the same but the totals will be lower.
