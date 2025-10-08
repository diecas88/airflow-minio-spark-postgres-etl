from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.providers.postgres.hooks.postgres import PostgresHook
import csv
import io
import boto3
import os
import time
import pandas as pd
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, current_timestamp, to_date, date_format, isnan, isnull
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import psycopg2
from sqlalchemy import create_engine

from credentials import GCP_PROJECT_ID, BQ_DATASET_TABLE, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="orders_dag",
    default_args=default_args,
    schedule=None,  
    catchup=False,
    tags=["postgres","minio","pyspark"],
) as dag:

    start_task = EmptyOperator(
        task_id="start",
        doc_md="This starts the airflow workflow"
    )

   
    def run_pyspark_etl():
        
        try:
            
            os.environ['AWS_ACCESS_KEY_ID'] = MINIO_ACCESS_KEY
            os.environ['AWS_SECRET_ACCESS_KEY'] = MINIO_SECRET_KEY
            os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
            
            spark = SparkSession.builder \
                .appName("ETL-orders") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .config("spark.executor.memory", "1g") \
                .config("spark.driver.memory", "1g") \
                .config("spark.sql.adaptive.skewJoin.enabled", "false") \
                .config("spark.sql.adaptive.localShuffleReader.enabled", "false") \
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                .config("spark.jars", "/opt/spark/jars/hadoop-aws-3.3.4.jar,/opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar") \
                .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
                .config("spark.hadoop.fs.s3a.path.style.access", "true") \
                .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
                .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
                .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
                .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
                .getOrCreate()
            
           
            products_df = spark.read \
                .option("header", "true") \
                .option("quote", "\"") \
                .option("sep", ",") \
                .csv(f"s3a://{MINIO_BUCKET_NAME}/raw_data/products/products.csv")
            
            products_with_timestamp = products_df.withColumn("current_timestamp", current_timestamp())

            
            orders_df = spark.read \
                .option("multiLine", "true") \
                .json(f"s3a://{MINIO_BUCKET_NAME}/raw_data/orders/orders.json")
            
            
            orders_transformed = orders_df \
                .withColumn("product_id", col("product.product_id")) \
                .withColumn("quantity_product", col("product.quantity")) \
                .withColumn("cash_or_card", 
                           when(col("credit_card").isNull(), "cash").otherwise("card")) \
                .withColumn("is_delivered", 
                           when(col("delivery_date").isNull(), 0).otherwise(1)) \
                .withColumn("order_date_formatted", 
                           date_format(to_date(col("order_date"), "M/d/yyyy"), "yyyy-MM-dd")) \
                .withColumn("delivery_date_formatted", 
                           date_format(to_date(col("delivery_date"), "M/d/yyyy"), "yyyy-MM-dd")) \
                .withColumn("current_timestamp", current_timestamp()) \
                .select(
                    col("id"),
                    col("customer_id"),
                    col("credit_card"),
                    col("order_date_formatted").alias("order_date"),
                    col("delivery_date_formatted").alias("delivery_date"),
                    col("cash_or_card"),
                    col("is_delivered"),
                    col("product_id"),
                    col("quantity_product"),
                    col("current_timestamp")
                )
            
            #
            products_output_path = f"s3a://{MINIO_BUCKET_NAME}/transformed_data/products/"
            products_with_timestamp.write \
                .mode("overwrite") \
                .option("compression", "snappy") \
                .parquet(products_output_path)
            
            orders_output_path = f"s3a://{MINIO_BUCKET_NAME}/transformed_data/orders/"
            orders_transformed.write \
                .mode("overwrite") \
                .option("compression", "snappy") \
                .parquet(orders_output_path)
           
            
            spark.stop()
            
            return "SUCCESS"
                
        except Exception as e:
            if 'spark' in locals():
                spark.stop()
            raise

    pyspark_etl_task = PythonOperator(
        task_id="run_pyspark_etl",
        python_callable=run_pyspark_etl,
        doc_md="PySpark ETL process"
    )

    def load_parquet_to_postgres():

        try:

            s3_client = boto3.client(
                's3',
                endpoint_url=MINIO_ENDPOINT,
                aws_access_key_id=MINIO_ACCESS_KEY,
                aws_secret_access_key=MINIO_SECRET_KEY,
                region_name='us-east-1'
            )
            
            postgres_conn = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
            engine = create_engine(postgres_conn)
            
            response = s3_client.list_objects_v2(Bucket=MINIO_BUCKET_NAME, Prefix="transformed_data/")
            
            products_response = s3_client.list_objects_v2(
                Bucket=MINIO_BUCKET_NAME,
                Prefix="transformed_data/products/"
            )
            
            products_parquet_key = None
            for obj in products_response['Contents']:
                if obj['Key'].endswith('.parquet'):
                    products_parquet_key = obj['Key']
                    break
            
            if not products_parquet_key:
                raise Exception("FAILED: No Parquet files found in products folder")
            
            products_obj = s3_client.get_object(Bucket=MINIO_BUCKET_NAME, Key=products_parquet_key)
            products_df = pd.read_parquet(io.BytesIO(products_obj['Body'].read()))
         
            # Load to PostgreSQL
            products_df.to_sql(
                'products', 
                engine, 
                schema='public', 
                if_exists='replace', 
                index=False,
                method='multi' 
            )
            
            
            orders_response = s3_client.list_objects_v2(
                Bucket=MINIO_BUCKET_NAME,
                Prefix="transformed_data/orders/"
            )
            
            if 'Contents' not in orders_response:
                raise Exception("FAILED: No orders files found in MinIO")
            
            
            orders_parquet_key = None
            for obj in orders_response['Contents']:
                if obj['Key'].endswith('.parquet'):
                    orders_parquet_key = obj['Key']
                    break
            
            if not orders_parquet_key:
                raise Exception("FAILED: No Parquet files found in orders folder")
            
            
            orders_obj = s3_client.get_object(Bucket=MINIO_BUCKET_NAME, Key=orders_parquet_key)
            orders_df = pd.read_parquet(io.BytesIO(orders_obj['Body'].read()))
            
            
            # Load to PostgreSQL
            orders_df.to_sql(
                'orders', 
                engine, 
                schema='public', 
                if_exists='replace', 
                index=False,
                method='multi'
            )

            return "SUCCESS"
            
        except Exception as e:
            return f"FAILED: {str(e)}"

    load_to_postgres_task = PythonOperator(
        task_id="load_parquet_to_postgres",
        python_callable=load_parquet_to_postgres,
        doc_md="Load Parquet files to PostgreSQL tables"
    )

    def insert_data_to_postgres():
        
        try:
            postgres_hook = PostgresHook(postgres_conn_id="postgres_default")
           
            bq_hook = BigQueryHook(gcp_conn_id="bigquery_default", use_legacy_sql=False, location="US")
            query = f"""
            SELECT 
                id, 
                first_name, 
                last_name, 
                email, 
                gender,
                phone, 
                country, 
                city, 
                FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%m/%d/%Y', birthday)) as birthday, 
                company, 
                department_comp, 
                job,
                CURRENT_TIMESTAMP() as load_date
            FROM `{GCP_PROJECT_ID}.{BQ_DATASET_TABLE}`
            """
            df = bq_hook.get_pandas_df(sql=query)
            
            df.to_sql(
                'customers',
                postgres_hook.get_sqlalchemy_engine(),
                if_exists='append',
                index=False,
                method='multi' 
            )

            return f"Successfully process"
            
        except Exception as e:
            print(f"ERROR inserting data to PostgreSQL: {e}")
            raise e


    insert_data_to_postgres = PythonOperator(
        task_id="insert_data_to_postgres",
        python_callable=insert_data_to_postgres,
        doc_md="Insert data to PostgreSQL"
    )

    def failed_task():
        print("PySpark ETL failed")
        return "Failed task"
    
    def success_task():
        print("PySpark ETL completed successfully")
        return "Success task"
    
    
    fail_handler = PythonOperator(
        task_id="failed_task",
        python_callable=failed_task,
        doc_md="Handle PySpark ETL failure",
        trigger_rule=TriggerRule.ONE_FAILED
    )

    
    success_handler = PythonOperator(
        task_id="success_task",
        python_callable=success_task,
        doc_md="Handle PySpark ETL success",
        trigger_rule=TriggerRule.ALL_SUCCESS
    )

    
    start_task >> insert_data_to_postgres >> pyspark_etl_task >> load_to_postgres_task >> [fail_handler, success_handler]