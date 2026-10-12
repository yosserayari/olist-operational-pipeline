# Olist Operational Pipeline

A Python and PostgreSQL project that loads e-commerce data, validates it, transforms it into business-oriented tables, and produces reporting-ready data.

## What it does

The pipeline takes nine CSV files from the Olist Brazilian E-Commerce dataset and loads them into PostgreSQL.

```text
CSV files
   ↓
Python ingestion
   ↓
raw → staging → mart → reporting
                       ↓
                  daily_sales
```

- **Raw:** source data loaded into PostgreSQL.
- **Staging:** consistent data types and standardized missing values.
- **Mart:** fact and dimension tables for orders, items, payments, reviews, customers, products and sellers.
- **Reporting:** a daily sales view for operational reporting.

## Tools

- Python
- PostgreSQL
- SQL
- Psycopg
- pytest
- Git and GitHub

## Project structure

```text
olist-operational-pipeline/
├── data/
│   └── raw/                  # Local CSV files (not committed)
├── docs/
│   ├── PROJECT_STATE.md
│   └── LEARNING_LOG.md
├── scripts/
│   └── run_pipeline.py       # Runs the pipeline
├── sql/
│   ├── raw_schema.sql
│   ├── staging/
│   │   └── build_staging.sql
│   ├── marts/
│   │   └── build_marts.sql
│   └── views/
│       └── build_reporting_views.sql
├── src/
│   ├── ingestion/
│   │   └── load_raw.py
│   └── validation/
│       ├── profile_relationships.py
│       ├── profile_source_data.py
│       └── data_quality_checks.py
├── tests/
│   └── test_pipeline_integrity.py
├── requirements.txt
└── README.md
```

## Setup

### 1. Prerequisites

Install Python, PostgreSQL and Git. The project has been developed and tested locally on Windows with PostgreSQL 18.

### 2. Create the database

Create a PostgreSQL database named `olist_pipeline` using pgAdmin or `psql`.

### 3. Configure the connection

Create a local `.env` file in the project root with your database connection settings:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olist_pipeline
DB_USER=postgres
DB_PASSWORD=your_local_password
```

Replace the values with your local PostgreSQL settings. Do not commit this file.

### 4. Install Python dependencies

From the project root, run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 5. Add the source data

Download the Olist Brazilian E-Commerce Public Dataset and place the nine CSV files in `data/raw/`.

The pipeline expects these filenames:

- `olist_customers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `product_category_name_translation.csv`

### 6. Run the pipeline

From the project root:

```powershell
python scripts/run_pipeline.py
```

The runner loads the raw CSV files, rebuilds staging, executes data-quality checks, builds the marts and recreates the reporting views. It then verifies key row counts.

**Warning:** this is a development pipeline. It reloads and rebuilds database tables, so run it only against the intended project database—not a production database.

## Run the tests

After the pipeline has completed successfully:

```powershell
python -m pytest -v
```

The current test suite contains eight tests covering row counts, key uniqueness, relationships, item-value calculations and daily reporting totals.

## Current validation results

A successful local run produced:

| Check | Result |
|---|---:|
| Orders | 99,441 |
| Order items | 112,650 |
| Payments | 103,886 |
| Reviews | 99,224 |
| Products | 32,951 |
| Daily sales reporting rows | 634 |
| Automated tests | 8 passed |

These counts describe the current dataset and are expected to change if the source data changes.

## Data-quality observations

The pipeline reports several source-data anomalies for investigation, including missing delivery timestamps, inconsistent timestamp sequences, non-positive product weights, invalid payment installment counts and orders without item records.

These records are not automatically corrected. A reported anomaly is not necessarily a confirmed business error; the appropriate treatment depends on the business rules.

## Current scope

The project demonstrates data ingestion, SQL transformation, relational modelling, data-quality checks and automated tests. Work remains to improve setup reproducibility, test failure handling and document business metric definitions.

The goal is to make the pipeline understandable and reproducible by another engineer, rather than simply produce a set of database tables.

PS : 
### Windows troubleshooting: Psycopg DLL error

On some Windows systems, application-control policies may block Psycopg's bundled binary extension.

If importing Psycopg fails with a DLL or `libpq` error:

1. Add `C:\Program Files\PostgreSQL\18\bin` to your Windows user `Path`.
2. Add a user environment variable named `PSYCOPG_IMPL` with the value `python`.
3. Restart VS Code.

Verify the selected implementation:

```powershell
python -c "import psycopg; print(psycopg.pq.__impl__)"
```

It should print `python`.

The pure-Python implementation still requires PostgreSQL's `libpq` client library. It is slower than the compiled implementations, but suitable for this local project. Most users won't need this workaround. See the [official Psycopg installation guide](https://www.psycopg.org/psycopg3/docs/basic/install.html).