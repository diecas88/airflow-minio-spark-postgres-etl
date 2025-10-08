CREATE TABLE public.customers (
  id BIGINT PRIMARY KEY,
  first_name VARCHAR(255), 
  last_name VARCHAR(255),
  email VARCHAR(255),
  gender VARCHAR(50),
  phone VARCHAR(50),
  country VARCHAR(100),
  city VARCHAR(100),
  birthday DATE,   
  company VARCHAR(100),
  department_comp VARCHAR(100),
  job VARCHAR(100),
  load_date TIMESTAMP
);

CREATE TABLE public.products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    description TEXT,
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.orders (
    id INTEGER PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    credit_card VARCHAR(20),
    order_date DATE NOT NULL,
    delivery_date DATE,
    cash_or_card VARCHAR(4) NOT NULL ,
    is_delivered INTEGER NOT NULL ,
    product_id INTEGER NOT NULL,
    quantity_product INTEGER NOT NULL,
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);