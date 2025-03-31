BEGIN;

-- Create sequences if they don't exist
CREATE SEQUENCE IF NOT EXISTS customer_id_seq;
CREATE SEQUENCE IF NOT EXISTS orders_id_seq;
CREATE SEQUENCE IF NOT EXISTS partoption_id_seq;
CREATE SEQUENCE IF NOT EXISTS preconfiguredproduct_id_seq;
CREATE SEQUENCE IF NOT EXISTS preconfiguredproductparts_id_seq;
CREATE SEQUENCE IF NOT EXISTS priceadjustmentrule_id_seq;
CREATE SEQUENCE IF NOT EXISTS category_id_seq;
CREATE SEQUENCE IF NOT EXISTS stock_id_seq;
CREATE SEQUENCE IF NOT EXISTS orderproduct_id_seq;
CREATE SEQUENCE IF NOT EXISTS orderitem_id_seq;
CREATE SEQUENCE IF NOT EXISTS part_id_seq;
CREATE SEQUENCE IF NOT EXISTS incompatibilityrule_id_seq;

CREATE TABLE IF NOT EXISTS public.customer (
    id integer NOT NULL DEFAULT nextval('customer_id_seq'::regclass),
    name character varying(255) NOT NULL,
    email character varying(255),
    phone character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT customer_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.orders (
    customer_id integer,
    id integer NOT NULL DEFAULT nextval('orders_id_seq'::regclass),
    total_price numeric(10, 2) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT orders_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.category (
    id integer NOT NULL DEFAULT nextval('category_id_seq'::regclass),
    name character varying(255) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT category_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.part (
    name character varying(255) NOT NULL,
    category_id integer NOT NULL,
    id integer NOT NULL DEFAULT nextval('part_id_seq'::regclass),
    CONSTRAINT part_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.partoption (
    part_id integer,
    id integer NOT NULL DEFAULT nextval('partoption_id_seq'::regclass),
    name character varying(255) NOT NULL,
    default_price numeric(10, 2) NOT NULL,
    CONSTRAINT partoption_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.preconfiguredproduct (
    category_id integer,
    id integer NOT NULL DEFAULT nextval('preconfiguredproduct_id_seq'::regclass),
    name character varying(255) NOT NULL,
    base_price numeric(10, 2) NOT NULL,
    CONSTRAINT preconfiguredproduct_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.preconfiguredproductparts (
    id integer NOT NULL DEFAULT nextval('preconfiguredproductparts_id_seq'::regclass),
    preconfigured_product_id integer,
    part_option_id integer,
    CONSTRAINT preconfiguredproductparts_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.priceadjustmentrule (
    id integer NOT NULL DEFAULT nextval('priceadjustmentrule_id_seq'::regclass),
    affected_option_id integer,
    condition_option_id integer,
    adjusted_price numeric(10, 2) NOT NULL,
    CONSTRAINT priceadjustmentrule_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.stock (
    id integer NOT NULL DEFAULT nextval('stock_id_seq'::regclass),
    part_option_id integer,
    quantity integer NOT NULL DEFAULT 0,
    CONSTRAINT stock_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.orderproduct (
    order_id integer NOT NULL,
    preconfigured_product_id integer,
    id integer NOT NULL DEFAULT nextval('orderproduct_id_seq'::regclass),
    custom_name character varying(255),
    base_product_name character varying(255) NOT NULL,
    CONSTRAINT orderproduct_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.orderitem (
    id integer NOT NULL DEFAULT nextval('orderitem_id_seq'::regclass),
    order_product_id integer NOT NULL,
    part_name character varying(255) NOT NULL,
    option_name character varying(255) NOT NULL,
    final_price numeric(10, 2) NOT NULL,
    CONSTRAINT orderitem_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.incompatibilityrule (
    id integer NOT NULL DEFAULT nextval('incompatibilityrule_id_seq'::regclass),
    part_option_id integer,
    incompatible_with_option_id integer,
    message text NOT NULL,
    CONSTRAINT incompatibilityrule_pkey PRIMARY KEY (id)
);

-- Add foreign key constraints
ALTER TABLE IF EXISTS public.orders
    ADD CONSTRAINT customer_id FOREIGN KEY (customer_id)
    REFERENCES public.customer (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.partoption
    ADD CONSTRAINT part_id FOREIGN KEY (part_id)
    REFERENCES public.part (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.preconfiguredproduct
    ADD CONSTRAINT category_id FOREIGN KEY (category_id)
    REFERENCES public.category (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.preconfiguredproductparts
    ADD CONSTRAINT preconfigured_product_id FOREIGN KEY (preconfigured_product_id)
    REFERENCES public.preconfiguredproduct (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.preconfiguredproductparts
    ADD CONSTRAINT part_option_id FOREIGN KEY (part_option_id)
    REFERENCES public.partoption (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.priceadjustmentrule
    ADD CONSTRAINT affected_option_id FOREIGN KEY (affected_option_id)
    REFERENCES public.partoption (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.priceadjustmentrule
    ADD CONSTRAINT condition_option_id FOREIGN KEY (condition_option_id)
    REFERENCES public.partoption (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.stock
    ADD CONSTRAINT part_option_id FOREIGN KEY (part_option_id)
    REFERENCES public.partoption (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.orderproduct
    ADD CONSTRAINT order_id FOREIGN KEY (order_id)
    REFERENCES public.orders (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.orderproduct
    ADD CONSTRAINT preconfigured_product_id FOREIGN KEY (preconfigured_product_id)
    REFERENCES public.preconfiguredproduct (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.orderitem
    ADD CONSTRAINT order_product_id FOREIGN KEY (order_product_id)
    REFERENCES public.orderproduct (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.part
    ADD CONSTRAINT category_id FOREIGN KEY (category_id)
    REFERENCES public.category (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.incompatibilityrule
    ADD CONSTRAINT part_option_id FOREIGN KEY (part_option_id)
    REFERENCES public.partoption (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS public.incompatibilityrule
    ADD CONSTRAINT incompatible_with_option_id FOREIGN KEY (incompatible_with_option_id)
    REFERENCES public.partoption (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
    NOT VALID;

-- Create indexes for performance optimization
-- Customer indexes
CREATE INDEX IF NOT EXISTS idx_customer_name ON customer(name);

-- Orders indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);

-- Part indexes
CREATE INDEX IF NOT EXISTS idx_part_category_id ON part(category_id);

-- PartOption indexes
CREATE INDEX IF NOT EXISTS idx_partoption_part_id ON partoption(part_id);

-- OrderProduct indexes
CREATE INDEX IF NOT EXISTS idx_orderproduct_order_id ON orderproduct(order_id);

-- PriceAdjustmentRule indexes
CREATE INDEX IF NOT EXISTS idx_price_adjustment_combo ON priceadjustmentrule(affected_option_id, condition_option_id);

-- IncompatibilityRule indexes
CREATE INDEX IF NOT EXISTS idx_incompatibility_rule ON incompatibilityrule(part_option_id, incompatible_with_option_id);

-- Create materialized views for analytics
-- 1. Top Preconfigured Products per Category
-- Shows top-selling preconfigured variations per base category
CREATE MATERIALIZED VIEW TopPreconfiguredProductsPerCategory AS
SELECT 
    pp.category_id,
    pp.id AS preconfigured_product_id,
    pp.name AS preconfigured_name,
    COUNT(op.id) AS times_ordered
FROM PreconfiguredProduct pp
JOIN OrderProduct op ON op.preconfigured_product_id = pp.id
GROUP BY pp.category_id, pp.id, pp.name
ORDER BY pp.category_id, times_ordered DESC;

-- To refresh this view periodically, run:
-- REFRESH MATERIALIZED VIEW TopPreconfiguredProductsPerCategory;

-- 2. Best-Selling Preconfigured Product (Top 1 Only)
-- Shows the single best-selling preconfigured product overall
CREATE MATERIALIZED VIEW BestSellingPreconfiguredProduct AS
SELECT 
    pp.id AS preconfigured_product_id,
    pp.name,
    COUNT(op.id) AS times_ordered
FROM PreconfiguredProduct pp
JOIN OrderProduct op ON op.preconfigured_product_id = pp.id
GROUP BY pp.id, pp.name
ORDER BY times_ordered DESC
LIMIT 1;

-- To refresh this view periodically, run:
-- REFRESH MATERIALIZED VIEW BestSellingPreconfiguredProduct;

END;
