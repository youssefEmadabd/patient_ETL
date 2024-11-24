# Use the official Apache Airflow image
FROM apache/airflow:2.7.1

# Install additional dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data/ /opt/airflow/data
COPY database_models/ /opt/airflow/database_models
COPY etl_process/ /opt/airflow/etl_process
COPY main.py /opt/airflow/main.py
COPY airflow/dags /opt/airflow/dags
