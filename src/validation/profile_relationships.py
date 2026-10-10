from pathlib import Path
import pandas as pd


DATA_DIR = Path("data/raw")


def load(name):
    return pd.read_csv(DATA_DIR / name)


def main():
    customers = load("olist_customers_dataset.csv")
    orders = load("olist_orders_dataset.csv")
    items = load("olist_order_items_dataset.csv")
    payments = load("olist_order_payments_dataset.csv")
    reviews = load("olist_order_reviews_dataset.csv")
    products = load("olist_products_dataset.csv")
    sellers = load("olist_sellers_dataset.csv")

    print("\n=== KEY UNIQUENESS ===")

    checks = {
        "customers.customer_id": customers["customer_id"].is_unique,
        "customers.customer_unique_id": customers["customer_unique_id"].is_unique,
        "orders.order_id": orders["order_id"].is_unique,
        "products.product_id": products["product_id"].is_unique,
        "sellers.seller_id": sellers["seller_id"].is_unique,
    }

    for key, result in checks.items():
        print(f"{key}: {result}")

    print("\n=== ONE-TO-MANY RELATIONSHIPS ===")

    print(
        "Orders with multiple items:",
        (items.groupby("order_id").size() > 1).sum()
    )

    print(
        "Orders with multiple payments:",
        (payments.groupby("order_id").size() > 1).sum()
    )

    print(
        "Orders with multiple reviews:",
        (reviews.groupby("order_id").size() > 1).sum()
    )

    print("\n=== CUSTOMER IDENTITY ===")

    customers_per_unique_id = (
        customers.groupby("customer_unique_id")["customer_id"]
        .nunique()
    )

    print(
        "Unique customers represented by multiple customer_ids:",
        (customers_per_unique_id > 1).sum()
    )

    print("\n=== FOREIGN KEY CHECKS ===")

    print(
        "Orders with unknown customer:",
        (~orders["customer_id"].isin(customers["customer_id"])).sum()
    )

    print(
        "Items with unknown order:",
        (~items["order_id"].isin(orders["order_id"])).sum()
    )

    print(
        "Items with unknown product:",
        (~items["product_id"].isin(products["product_id"])).sum()
    )

    print(
        "Items with unknown seller:",
        (~items["seller_id"].isin(sellers["seller_id"])).sum()
    )

    print(
        "Payments with unknown order:",
        (~payments["order_id"].isin(orders["order_id"])).sum()
    )

    print(
        "Reviews with unknown order:",
        (~reviews["order_id"].isin(orders["order_id"])).sum()
    )
        
    print("\n=== MULTIPLE REVIEWS ===")

    review_counts = reviews.groupby("order_id").size()

    print(
        "Maximum reviews for one order:",
        review_counts.max()
    )

    print(
        "Orders with exactly 2 reviews:",
        (review_counts == 2).sum()
    )

    print("\n=== CUSTOMER IDENTITY EXAMPLES ===")

    multiple_ids = (
        customers.groupby("customer_unique_id")["customer_id"]
        .unique()
    )
    print("\n=== REVIEW ID ANALYSIS ===")

    print(
        "Unique review IDs:",
        reviews["review_id"].nunique()
    )

    print(
        "Duplicate review ID rows:",
        reviews["review_id"].duplicated().sum()
    )

    print(
        "Orders with multiple distinct review IDs:",
        (
            reviews.groupby("order_id")["review_id"]
            .nunique() > 1
        ).sum()
    )

    examples = multiple_ids[multiple_ids.apply(len) > 1].head(5)

    for unique_id, customer_ids in examples.items():
        print(f"{unique_id} -> {list(customer_ids)}")


if __name__ == "__main__":
    main()