CREATE TABLE IF NOT EXISTS public.etl_watermarks (
    pipeline_name VARCHAR(100) PRIMARY KEY,
    last_updated_at TIMESTAMP(3) NOT NULL
);


INSERT INTO public.etl_watermarks (
    pipeline_name,
    last_updated_at
)
VALUES (
    'mssql_orders_to_postgres',
    '1900-01-01 00:00:00.000'
)
ON CONFLICT (pipeline_name) DO NOTHING;


SELECT *
FROM public.etl_watermarks;