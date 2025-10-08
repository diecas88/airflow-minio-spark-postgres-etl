# 🚀 Airflow Castor - ETL Project with Apache Airflow

[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)](https://airflow.apache.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)
[![PySpark](https://img.shields.io/badge/PySpark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white)](https://spark.apache.org/)

## 📋 Description

This project implements an ETL (Extract, Transform, Load) pipeline using Apache Airflow, PySpark, MinIO, and PostgreSQL. The system processes orders and products data, performing transformations with PySpark and storing the results in a PostgreSQL database.

## 🏗️ Architecture

The project consists of the following components:

- 🔄 **Apache Airflow**: Workflow orchestrator
- ⚡ **PySpark**: Data processing engine for ETL
- 🗄️ **MinIO**: S3-compatible object storage
- 🐘 **PostgreSQL**: Relational database for storing processed data
- ☁️ **BigQuery**: Customer data source (Google Cloud)

## ✨ Key Features

- 🔄 **Complete ETL Pipeline**: Data extraction, transformation, and loading
- ⚡ **PySpark Processing**: Distributed and scalable transformations
- 💾 **Hybrid Storage**: MinIO for intermediate data, PostgreSQL for final data
- ☁️ **BigQuery Integration**: Customer data extraction from Google Cloud
- 🛡️ **Error Handling**: Success and failure tasks with trigger rules
- 📦 **Data Compression**: Optimized storage with Parquet format
- 🔧 **Docker Support**: Containerized deployment
- 📊 **Real-time Monitoring**: Comprehensive logging and monitoring

## 📁 Project Structure

```
airflow-castor/
├── 📂 dags/
│   ├── 🐍 orders_dag.py          # Main orders processing DAG
│   └── 🔐 credentials.py         # Credentials configuration
├── 📂 queries/
│   ├── 🗃️ customers_bigquery.sql # BigQuery SQL query
│   ├── 📊 kpis.sql              # KPI queries
│   ├── 📄 orders.json           # Sample orders data
│   ├── 🗄️ postgres_tables.sql   # Table creation scripts
│   └── 📋 products.csv          # Products data
├── 📂 include/
│   └── 🔑 bigquery-course-464012-acf411040090.json # GCP credentials
├── 🐳 docker-compose.yml        # PostgreSQL configuration
├── 🐳 docker-compose.override.yml # MinIO configuration
├── 🐳 Dockerfile               # Custom image with Java and AWS JARs
├── 📦 requirements.txt         # Python dependencies
├── 📦 packages.txt            # System packages
└── 📄 README.md               # Project documentation
```

## 🛠️ Technologies Used

### 🔧 Core
- 🔄 **Apache Airflow 2.x**: Workflow orchestration
- 🐍 **Python 3.x**: Main programming language
- ⚡ **PySpark 3.5.4**: Distributed data processing

### 💾 Storage
- 🗄️ **MinIO**: S3-compatible object storage
- 🐘 **PostgreSQL 15**: Relational database
- ☁️ **Google BigQuery**: Cloud data warehouse

### 📊 Data Processing
- 🐼 **Pandas**: Data manipulation
- 🏹 **PyArrow**: Parquet file processing
- 🔗 **Boto3**: AWS client for MinIO
- 📦 **SQLAlchemy**: Database ORM

## 📊 Data Flow

1. **📥 Extraction**: 
   - 📋 Product data from MinIO (CSV)
   - 📄 Orders data from MinIO (JSON)
   - 👥 Customer data from BigQuery

2. **🔄 Transformation**:
   - ⚡ Processing with PySpark
   - 🧹 Data cleaning and normalization
   - 📅 Date and field formatting
   - 📦 Snappy compression

3. **📤 Loading**:
   - 💾 Temporary storage in MinIO (Parquet)
   - 🐘 Final load to PostgreSQL
   - 🗄️ Table creation: `products`, `orders`, `customers`

## 🚀 Installation and Configuration

### 📋 Prerequisites

- 🐳 Docker and Docker Compose
- 🐍 Python 3.8+
- ☁️ Google Cloud Platform access (for BigQuery)
- ☕ Java 17+ (for PySpark)

### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd airflow-castor
```

### 2️⃣ Configure Credentials

Edit the `dags/credentials.py` file with your credentials:

```python
# MinIO configuration
MINIO_ENDPOINT = "http://host.docker.internal:9000"
MINIO_ACCESS_KEY = "minio"
MINIO_SECRET_KEY = "minio12345"
MINIO_BUCKET_NAME = "orders"

# PostgreSQL configuration
POSTGRES_HOST = "airflow-castor_0f1e85-postgres-1"
POSTGRES_PORT = "5432"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_DB = "postgres"

# BigQuery configuration
GCP_PROJECT_ID = "your-gcp-project"
BQ_DATASET_TABLE = "airflow.customers"
```

### 3️⃣ Configure Docker Network

```bash
docker network create airflow
```

### 4️⃣ Start Services

```bash
# Start PostgreSQL
docker-compose up -d

# Start MinIO
docker-compose -f docker-compose.override.yml up -d
```

### 5️⃣ Configure MinIO

Access the MinIO console at `http://localhost:9001` and create the `orders` bucket.

### 6️⃣ Load Sample Data

Upload files from `queries/` to the MinIO bucket:
- 📋 `products.csv` → `raw_data/products/`
- 📄 `orders.json` → `raw_data/orders/`

## ⚙️ Airflow Configuration

### 🔧 Environment Variables

Configure the following variables in Airflow:

- 🐘 `postgres_default`: PostgreSQL connection
- ☁️ `bigquery_default`: BigQuery connection
- 🗄️ `aws_default`: MinIO connection (using MinIO credentials)

### 🔗 Required Connections

1. 🐘 **PostgreSQL**: `postgres_default`
2. ☁️ **BigQuery**: `bigquery_default`
3. 🗄️ **AWS/MinIO**: `aws_default`

### 🔐 Connection Details

#### PostgreSQL Connection
- **Connection ID**: `postgres_default`
- **Connection Type**: `Postgres`
- **Host**: `airflow-castor_0f1e85-postgres-1`
- **Schema**: `postgres`
- **Login**: `postgres`
- **Password**: `postgres`
- **Port**: `5432`

#### BigQuery Connection
- **Connection ID**: `bigquery_default`
- **Connection Type**: `Google Cloud`
- **Project ID**: Your GCP project ID
- **Keyfile JSON**: Path to your service account JSON

#### MinIO Connection
- **Connection ID**: `aws_default`
- **Connection Type**: `Amazon Web Services`
- **Login**: `minio`
- **Password**: `minio12345`
- **Extra**: `{"endpoint_url": "http://host.docker.internal:9000"}`

## 📈 Monitoring and Logs

- 🌐 **Airflow UI**: `http://localhost:8080`
- 🗄️ **MinIO Console**: `http://localhost:9001`
- 📋 **Logs**: Available in the Airflow interface
- 📊 **DAG Status**: Monitor task execution in real-time

## 🔄 DAG Tasks

### `orders_dag`

1. 🚀 **start**: Initial task
2. 👥 **insert_data_to_postgres**: Customer data extraction from BigQuery
3. ⚡ **run_pyspark_etl**: ETL processing with PySpark
4. 📤 **load_parquet_to_postgres**: Loading transformed data to PostgreSQL
5. ✅ **success_task**: Success handling
6. ❌ **failed_task**: Error handling

### 📋 Task Dependencies

```
start → insert_data_to_postgres → run_pyspark_etl → load_parquet_to_postgres
                                                      ↓
                                              [success_task, failed_task]
```

## 🗄️ Data Structure

### 📦 `products` Table
- 📋 Product fields with metadata
- ⏰ Load timestamp
- 🆔 Primary key: `product_id`

### 📄 `orders` Table
- 🔄 Transformed order information
- 🧮 Calculated fields: `cash_or_card`, `is_delivered`
- 📅 Normalized dates
- 🆔 Primary key: `id`

### 👥 `customers` Table
- 👤 Customer data from BigQuery
- 📊 Demographic and contact information
- 🆔 Primary key: `id`

## 🐛 Troubleshooting

### ⚠️ Common Issues

1. **🗄️ MinIO connection error**:
   - ✅ Verify that MinIO is running
   - 🔐 Check credentials in `credentials.py`
   - 🌐 Ensure network connectivity

2. **⚡ PySpark error**:
   - ☕ Verify that Java 17+ is installed
   - 📦 Check AWS JARs in `/opt/spark/jars/`
   - 💾 Ensure sufficient memory allocation

3. **🐘 PostgreSQL error**:
   - ✅ Verify that the database is running
   - 🌐 Check Docker network configuration
   - 🔐 Verify connection credentials

4. **☁️ BigQuery error**:
   - 🔑 Check GCP service account permissions
   - 📄 Verify JSON credentials file
   - 🌐 Ensure network access to Google Cloud

### 📋 Useful Logs

```bash
# Airflow logs
docker logs <airflow-container>

# MinIO logs
docker logs airflow_minio1

# PostgreSQL logs
docker logs airflow_postgres

# Check container status
docker ps -a
```

### 🔧 Performance Optimization

- ⚡ **Spark Configuration**: Adjust memory settings in PySpark
- 💾 **Database Tuning**: Optimize PostgreSQL settings
- 📦 **Compression**: Use appropriate compression for Parquet files
- 🔄 **Parallel Processing**: Configure task parallelism

## 🧪 Testing

### 🧪 Unit Tests

```bash
# Run DAG tests
python -m pytest tests/dags/

# Test individual components
python -m pytest tests/dags/test_orders_dag.py
```

### 🔍 Integration Tests

```bash
# Test database connections
python tests/test_connections.py

# Test data pipeline
python tests/test_etl_pipeline.py
```

## 📊 Performance Metrics

- ⏱️ **Processing Time**: Monitor ETL execution time
- 📈 **Data Volume**: Track data processing capacity
- 🔄 **Success Rate**: Monitor task success/failure rates
- 💾 **Resource Usage**: CPU, memory, and storage utilization

## 🔒 Security Considerations

- 🔐 **Credentials**: Store sensitive data in environment variables
- 🌐 **Network Security**: Use secure connections for production
- 🔑 **Access Control**: Implement proper authentication
- 📋 **Audit Logging**: Enable comprehensive logging

## 📄 License

This project is under the MIT License. See the `LICENSE` file for more details.

## 👥 Authors

- **Diego Castellanos** - *Initial Development* - [GitHub](https://github.com/diego)

## 🤝 Contributing

1. 🍴 Fork the project
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔀 Open a Pull Request

## 🙏 Acknowledgments

- 🔄 Apache Airflow Community
- ⚡ PySpark Documentation
- 🗄️ MinIO Documentation
- 🐘 PostgreSQL Community
- ☁️ Google Cloud Platform

## 📚 Additional Resources

- 📖 [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- ⚡ [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- 🗄️ [MinIO Documentation](https://docs.min.io/)
- 🐘 [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**⚠️ Note**: This project is an educational example of ETL implementation with Apache Airflow. Make sure to configure the appropriate credentials before using in production.

**🚀 Happy Data Processing!** 🎉