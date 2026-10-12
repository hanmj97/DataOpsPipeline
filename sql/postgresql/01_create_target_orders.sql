CREATE TABLE IF NOT EXISTS public.etl_orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(50) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    updated_at TIMESTAMP(3) NOT NULL
);