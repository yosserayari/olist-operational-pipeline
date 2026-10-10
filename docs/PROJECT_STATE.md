# Project State

**Last updated:** 2026-10-10

## 1. Career objective

Target profile: **Junior Data Engineer — Data Integration & Automation**.

Build reliable systems that ingest data, validate and transform it, and deliver trustworthy datasets or automated business workflows.

Technical focus: Python, SQL, PostgreSQL, APIs, data quality, data modelling, testing, automation and deployment.

## 2. Project objective

Build a realistic, reproducible data pipeline using the Olist Brazilian E-Commerce Public Dataset.

The dataset is Brazilian. It is being used to demonstrate transferable engineering skills, not to make claims about the Tunisian market.

Final deliverable: working code and SQL, database models, repeatable quality checks, documented assumptions, reliable execution, and business-facing reports.

## 3. Architecture

Source CSV files → raw → staging → mart → reporting

- **Raw:** Preserve source data. The nine source tables currently use TEXT columns.
- **Staging:** Convert data types, standardize missing values and prepare source tables for modelling.
- **Mart:** Create business-oriented fact and dimension tables.
- **Reporting:** Expose useful business metrics through database views.

## 4. Current implementation

### Raw tables
Nine tables loaded into PostgreSQL:
customers, geolocation, orders, order_items, order_payments, order_reviews, products, sellers, category_translation.

### Staging tables
Eight tables built through `sql/staging/build_staging.sql`:
orders, order_items, products, customers, order_payments, sellers, order_reviews, category_translation.

Geolocation remains in raw because it is not yet needed for the current use cases.

### Mart tables
Defined in `sql/marts/build_marts.sql`:
- `mart.fact_orders`
- `mart.fact_order_items`
- `mart.fact_payments`
- `mart.fact_reviews`
- `mart.dim_customers`
- `mart.dim_products`
- `mart.dim_sellers`

### Reporting
`reporting.daily_sales`, defined in `sql/views/build_reporting_views.sql`.

It includes daily order counts, delivered and active orders, orders without item records, item value, freight value, gross order value and average delivered order value.

## 5. Verified findings

- Raw orders: 99,441 rows.
- Raw order items: 112,650 rows.
- Raw payments: 103,886 rows.
- Raw reviews: 99,224 rows.
- Raw products: 32,951 rows.
- Raw customers: 99,441 rows.
- Raw sellers: 3,095 rows.
- Category translations: 71 rows.
- Geolocation: approximately 1 million rows.

Data-quality findings identified so far:
- 8 delivered orders have no customer-delivery timestamp.
- 189 orders have timestamp-sequence violations under our current rule.
- 7,826 delivered orders were flagged as late against the estimated delivery date.
- 4 products have non-positive weights.
- 2 payment rows have non-positive installment counts.
- 623 products have no English category translation.
- 814 review rows have review IDs that are not unique; the exact nature of these duplicates has not yet been confirmed.
- 775 orders have no matching item record.
- Payment reconciliation found 303 differences greater than 0.01 among 98,665 orders with both item and payment records. The total signed difference was 2,870.39.

These findings are not all confirmed business errors. Preserve source data and document the meaning of each rule before making corrections.

## 6. Engineering lessons

- A NULL must be interpreted in business context.
- Table grain must be explicit.
- Joining multiple one-to-many tables before aggregation can multiply totals.
- Raw values should not be silently repaired.
- SQL that executes successfully still needs validation.
- Reporting metrics need documented business definitions.

## 7. Current state and next action

The raw, staging, mart and first reporting layers have been built and inspected.

**Next:** verify Git status and save any pending source changes. Then review the current pipeline against the final deliverable requirements before adding more features. Do not add another reporting view until its value and purpose are clear.

## 8. Important project paths

- `src/ingestion/load_raw.py`
- `sql/staging/build_staging.sql`
- `sql/marts/build_marts.sql`
- `sql/views/build_reporting_views.sql`
- `docs/PROJECT_STATE.md`
- `docs/LEARNING_LOG.md`

Database: `olist_pipeline`

Do not record database passwords or `.env` contents in documentation.

## 9. Restart instructions

When resuming after a break:
1. Read this file.
2. Check `git status`.
3. Inspect the relevant source code before changing it.
4. Confirm the latest database state where necessary.
5. Continue from the stated next action without repeating completed work.