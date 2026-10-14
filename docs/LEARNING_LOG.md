# Learning Log

This records skills I am developing, not merely tasks I have completed.

## Session: 2026-10-08 to 2026-10-10

### 1. Data pipeline architecture
**Concept:** raw → staging → mart → reporting.

- Raw preserves source data.
- Staging converts types and prepares data for use.
- Marts model business entities and events.
- Reporting exposes metrics for users.

**Practice check:** Explain why these layers have different responsibilities and when a smaller project might not need all of them.

### 2. Data profiling and quality
**Concept:** Missing values, unusual values and inconsistent timestamps must be interpreted in context.

We identified missing delivery dates, timestamp-order violations, untranslated categories and invalid measurements.

**Practice check:** Explain why a missing delivery timestamp is more suspicious for a delivered order than for a cancelled order.

### 3. Data types and transformations
**Concept:** Raw columns were loaded as TEXT. Staging converts them to TIMESTAMP, INTEGER and NUMERIC where appropriate.

A product field containing text such as `40.0` could not be cast directly to INTEGER, so we converted it through NUMERIC.

**Practice check:** Explain why raw and staging can represent the same value differently.

### 4. Table grain and relationship cardinality
**Concept:** Different tables represent different things.

- `fact_orders`: one row per order.
- `fact_order_items`: one row per item within an order.
- `fact_payments`: one row per payment record.
- `fact_reviews`: one row per review record.

Joining multiple one-to-many tables before aggregation can multiply values.

**Practice check:** Explain how three items and two payment records can produce six joined rows, and how to prevent incorrect totals.

### 5. Business metrics and assumptions
**Concept:** A valid SQL calculation is not automatically a valid business metric.

For example, item price plus freight is our current gross order value calculation. Its official business interpretation must be documented and confirmed before making accounting or revenue claims.

**Practice check:** Explain the distinction between a formula, a metric definition and a business requirement.

## Template for future sessions

#### Automated data-quality checks

**What I built:** SQL checks for key uniqueness, referential integrity, valid values and known anomalies, integrated into the pipeline runner.

**Why:** Successful execution and matching row counts alone do not prove the data is valid.

**Important distinction:** Core failures stop the pipeline; known anomalies are reported for investigation instead of silently changing the data.

**Practice check:** Explain why a missing foreign key should fail a core check, while an unusual delivery timestamp might be reported for investigation.

**Next practice task:** Add automated tests that verify the pipeline's outputs and failure behavior.

Update this log honestly. Completing a task does not automatically mean I understand the concept. Use the practice checks to identify what needs revisiting.

### Testing quality-check behavior

Added two tests using a fake database connection.

- A critical quality-check failure raises an error.
- A warning is reported without failing the check run.

The test suite now has 10 passing tests.

**Next practice:** explain how a critical error prevents the pipeline from continuing to build downstream models.

### Pipeline failure handling

Added a test that simulates a critical data-quality failure and checks
that the runner stops before building the marts and reporting views.

The test uses mocked connections, so it does not modify the real database.

**Lesson:** Testing an individual function is different from testing how
the pipeline behaves when that function fails.

**Current result:** 11 tests passed.

### Database transactions

**What I learned:** A transaction groups database changes so they
can be committed together or rolled back when a step fails.

**Why it matters:** A failed pipeline should not leave a partially
rebuilt database.

**Practice question:** What could happen if raw ingestion commits
successfully but a later data-quality check fails?f

### Business-ready reporting metrics

Improved `reporting.daily_sales` to distinguish in-progress, canceled,
unavailable and delivered orders, and to report delivered product,
freight and gross order values separately from all recorded orders.

Added a test comparing delivered product value and delivered order
counts against the underlying mart tables.

Current result: 13 tests passed.

Important distinction: delivered gross order value is not profit or
verified cash collected.