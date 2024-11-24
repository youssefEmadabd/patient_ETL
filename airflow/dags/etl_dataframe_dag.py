import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
sys.path.insert(0,"/Users/youssefemad/Documents/patient_ETL")
from main import extract, transform, load  # Replace with your actual function file

default_args = {
    "owner": "youssef",
    "depends_on_past": False,
    "retries": 1,
}

# Define the DAG
with DAG(
    "etl_dataframe_dag",
    default_args=default_args,
    description="ETL pipeline with DataFrame transformations",
    schedule_interval=None,  # Manually triggered
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Extract
    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract
    )

    # Task 2: Transform
    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform,
        provide_context=True
    )

    # Task 3: Load
    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
        provide_context=True
    )

    # Define task dependencies
    extract_task >> transform_task >> load_task
