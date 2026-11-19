# GrowthLab — Customer Behaviour, Retention & Experimentation Analytics

**Python · DuckDB · SQL · Tableau · Statistical testing**

GrowthLab analyzes two months of historical cosmetics-store e-commerce events to study shopping activity, repeat purchasing, purchase-value trends, and customer segments. A **separate, explicitly synthetic randomized A/B test** demonstrates experiment evaluation; no real A/B assignment is present in the historical data.

## Results

| KPI | Result |
|---|---:|
| Cleaned event records | 7,797,981 |
| Active users | 725,736 |
| Purchasing users | 49,861 |
| Purchase-item events | 476,919 |
| Recorded purchase value (source price units) | 2,400,858.75 |
| December purchasers also purchasing in January | 15.51% |

**Definitions matter:** each purchase event represents a product interaction, not necessarily a separate order; the session funnel measures **presence of view, cart and purchase events in a session**, not a verified chronological journey. A first observed purchase is not necessarily a customer's first-ever purchase. Price currency is unverified.

## Tableau dashboards

The packaged [Tableau workbook](tableau/GrowthLab_Analytics_Final.twbx) contains **three dashboards** supported by eight aggregated data extracts:

| Dashboard | Focus |
|---|---|
| Executive Overview | Users, item-level purchases, recorded purchase value, daily trend and labeled category ranking |
| Customer Behaviour | Session-stage funnel, purchaser retention heatmap and RFM segmentation |
| Experimentation Analytics | Synthetic conversion comparison, treatment uplift and statistical evidence |

For a labeled-category example, see the [Tableau category view](assets/screenshots/13_tableau_executive_charts.png). The category analysis omits `Unclassified`, which represents approximately **96.1% of recorded purchase value**; labeled-category rankings are therefore not representative of the full product mix.

## Simulated experiment (separate dataset)

![Simulated Control vs Treatment purchase conversion rates, with confidence intervals](assets/charts/ab_test_conversion.png)

40,000 synthetic visitors were randomly assigned 50:50 to two checkout variants with a fixed random seed. The observed simulated conversion rates are **8.175% Control** and **9.340% Treatment**, a **+1.165 percentage-point** difference (**+14.25% relative**). Two-sided two-proportion z-test: *p* = **0.00003767**; 95% CI for treatment minus control: **+0.611 to +1.719 percentage points**. These results demonstrate analysis technique only and **do not establish a real-world checkout improvement**.

## Pipeline

- **`scripts/`**: source verification, ingestion, data quality, aggregate exports, synthetic experiment generation and test evaluation
- **`sql/`**: quality checks, KPIs, session funnel, retention cohorts, RFM, daily purchase value and category performance
- **`tableau/exports/`**: eight aggregate CSVs used by the Tableau workbook (no per-user records)
- **`docs/`**: source description and analytical-methodology details

To reproduce with Python 3.11+ after obtaining the source December 2019 and January 2020 archives:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python scripts/00_verify_data.py
python scripts/01_ingest_data.py
python scripts/02_profile_data.py
python scripts/03_clean_data.py
python scripts/04_run_quality_sql.py
python scripts/05_run_customer_analytics.py
python scripts/06_generate_ab_experiment.py
python scripts/07_analyze_ab_experiment.py
```

Input archives must be named `2019-Dec.csv.gz` and `2020-Jan.csv.gz` in `data/raw/`. Source-level event data and the local DuckDB database are **not distributed** in this repository. The Tableau workbook includes only the aggregate extracts; `tableau/exports/` contains regenerable aggregate CSVs.

## Data source and limitations

Dataset: [eCommerce Events History in Cosmetics Shop (Kaggle)](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop), shared by Michael Kechinov with credit to [REES46](https://rees46.com/en/datasets). Raw event files are not redistributed. The dataset publisher requests source attribution.

This project covers **December 2019–January 2020** only. Missing category labels, short retention follow-up, unknown price currency, and lack of verified unique order identifiers constrain the conclusions. The experiment is simulated and independently generated.
