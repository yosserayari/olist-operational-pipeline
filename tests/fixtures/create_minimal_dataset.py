import csv
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent / "olist_minimal"

DATA = {
    "olist_customers_dataset.csv": (
        [
            "customer_id", "customer_unique_id",
            "customer_zip_code_prefix", "customer_city",
            "customer_state",
        ],
        [["CUST-1", "UNIQUE-1", "12345", "sao_paulo", "SP"]],
    ),
    "olist_geolocation_dataset.csv": (
        [
            "geolocation_zip_code_prefix", "geolocation_lat",
            "geolocation_lng", "geolocation_city",
            "geolocation_state",
        ],
        [["12345", "-23.55", "-46.63", "sao_paulo", "SP"]],
    ),
    "olist_orders_dataset.csv": (
        [
            "order_id", "customer_id", "order_status",
            "order_purchase_timestamp", "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        [[
            "ORDER-1", "CUST-1", "delivered",
            "2017-01-01 10:00:00",
            "2017-01-01 10:15:00",
            "2017-01-02 10:00:00",
            "2017-01-03 10:00:00",
            "2017-01-05 10:00:00",
        ]],
    ),
    "olist_order_items_dataset.csv": (
        [
            "order_id", "order_item_id", "product_id",
            "seller_id", "shipping_limit_date",
            "price", "freight_value",
        ],
        [["ORDER-1", "1", "PROD-1", "SELLER-1",
          "2017-01-02 08:00:00", "100.00", "10.00"]],
    ),
    "olist_order_payments_dataset.csv": (
        [
            "order_id", "payment_sequential", "payment_type",
            "payment_installments", "payment_value",
        ],
        [["ORDER-1", "1", "credit_card", "1", "110.00"]],
    ),
    "olist_order_reviews_dataset.csv": (
        [
            "review_id", "order_id", "review_score",
            "review_comment_title", "review_comment_message",
            "review_creation_date", "review_answer_timestamp",
        ],
        [["REVIEW-1", "ORDER-1", "5", "Good",
          "Good delivery", "2017-01-04 10:00:00",
          "2017-01-05 10:00:00"]],
    ),
    "olist_products_dataset.csv": (
        [
            "product_id", "product_category_name",
            "product_name_lenght", "product_description_lenght",
            "product_photos_qty", "product_weight_g",
            "product_length_cm", "product_height_cm",
            "product_width_cm",
        ],
        [["PROD-1", "beleza_saude", "20", "100",
          "1", "500", "10", "10", "10"]],
    ),
    "olist_sellers_dataset.csv": (
        [
            "seller_id", "seller_zip_code_prefix",
            "seller_city", "seller_state",
        ],
        [["SELLER-1", "12345", "sao_paulo", "SP"]],
    ),
    "product_category_name_translation.csv": (
        ["product_category_name", "product_category_name_english"],
        [["beleza_saude", "health_beauty"]],
    ),
}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    for filename, (headers, rows) in DATA.items():
        path = OUTPUT / filename

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

    print(f"Created {len(DATA)} fixture CSV files in {OUTPUT}")


if __name__ == "__main__":
    main()