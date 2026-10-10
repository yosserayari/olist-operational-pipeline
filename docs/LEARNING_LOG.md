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

### Session date
**Objective:**

**What I built:**

**Why it was needed:**

**Decision or trade-off:**

**Problem encountered and how it was resolved:**

**What I can explain without notes:**

**What I still don't understand:**

**Next practice task:**

---

Update this log honestly. Completing a task does not automatically mean I understand the concept. Use the practice checks to identify what needs revisiting.