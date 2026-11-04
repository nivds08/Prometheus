"""
Run the full data pipeline end-to-end:
  1. Load raw theLook eCommerce CSVs into DuckDB
  2. Run advanced SQL analytics (cohort retention, RFM, category margins, monthly KPIs)
  3. Run the ML pipeline (K-Means segmentation + Random Forest churn model)

Usage:  python run_pipeline.py

This file is a batch pipeline, not the dashboard. To open the UI:
  streamlit run dashboard/app.py
"""
import runpy
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _running_under_streamlit():
    return bool(os.environ.get("STREAMLIT_SERVER_PORT") or os.environ.get("STREAMLIT_RUNTIME"))


def run(label, script_path, cwd):
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    old_cwd = os.getcwd()
    old_path = sys.path[:]
    try:
        os.chdir(cwd)
        sys.path.insert(0, cwd)
        runpy.run_path(script_path, run_name="__main__")
    finally:
        os.chdir(old_cwd)
        sys.path = old_path


if __name__ == "__main__":
    if _running_under_streamlit():
        import streamlit as st
        st.set_page_config(page_title="Wrong file", layout="centered")
        st.error("You ran the data pipeline with Streamlit. This file is not the dashboard.")
        st.markdown(
            """
            Use these commands in a normal terminal instead:

            1. Install packages once: `pip install -r requirements.txt`
            2. Build the warehouse: `python run_pipeline.py`
            3. Open the dashboard: `streamlit run dashboard/app.py`
            """
        )
        st.stop()

    try:
        import duckdb  # noqa: F401
    except ImportError:
        sys.exit(
            "Missing package: duckdb\n"
            "Install dependencies first:\n"
            "  python -m pip install -r requirements.txt\n"
            "Then run:\n"
            "  python run_pipeline.py"
        )

    ecommerce_dir = os.path.join(BASE_DIR, "ecommerce")
    required_csvs = [
        "distribution_centers.csv",
        "products.csv",
        "users.csv",
        "orders.csv",
        "order_items.csv",
        "inventory_items.csv",
        "events.csv",
    ]
    missing = [name for name in required_csvs if not os.path.isfile(os.path.join(ecommerce_dir, name))]
    if missing:
        print("Raw CSVs not found. Generating a local demo dataset...")
        run(
            "STEP 0/3: Generate demo CSVs",
            os.path.join(BASE_DIR, "scripts", "generate_sample_data.py"),
            os.path.join(BASE_DIR, "scripts"),
        )

    run("STEP 1/3: Load CSVs into DuckDB", os.path.join(BASE_DIR, "scripts", "load_to_duckdb.py"), os.path.join(BASE_DIR, "scripts"))
    run("STEP 2/3: Run SQL analytics (cohort, RFM, category margins, KPIs)", os.path.join(BASE_DIR, "scripts", "run_analytics.py"), os.path.join(BASE_DIR, "scripts"))
    run("STEP 3/3: Run ML pipeline (K-Means segmentation + churn model)", os.path.join(BASE_DIR, "ml", "churn_segmentation.py"), os.path.join(BASE_DIR, "ml"))
    print(f"\n{'='*70}\nPipeline complete. Launch the dashboard with:\n"
          f"  cd dashboard && streamlit run app.py\n{'='*70}")
