from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

import requests
import pandas as pd
import time
from pymongo import MongoClient

headers = {
    'authority': 'www.scrapethissite.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-GB,en;q=0.8',
    'referer': 'https://www.scrapethissite.com/pages/forms/?per_page=100',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

params = {
    'page_num': '1',
    'per_page': '100',
}

def scrape_page(page_num, **kwargs):
    params['page_num'] = str(page_num)
    response = requests.get('https://www.scrapethissite.com/pages/forms/', params=params, headers=headers)
    html_content = response.content
    time.sleep(1)
    table = pd.read_html(html_content)[0]
    return table

def concat_tables(**kwargs):
    ti = kwargs['ti']
    result_df_list = [ti.xcom_pull(task_ids=f'scrape_page_{i}') for i in range(page_limit)]

    # Check if any XCom value is None
    if any(result_df is None for result_df in result_df_list):
        raise ValueError("XCom value is None. Check if the previous tasks completed successfully.")
    
    result_df = pd.concat(result_df_list, ignore_index=True)
    result_df.to_csv('/opt/airflow_app/output/NHL_team_stats.csv')
    return result_df

def save_to_mongodb(**kwargs):
    ti = kwargs['ti']
    result_df = ti.xcom_pull(task_ids='concat_tables')

    # Convert the DataFrame to a MongoDB-friendly format
    records = result_df.to_dict(orient='records')

    # Save to MongoDB
    client = MongoClient('mongodb://host.docker.internal:27017/')
    db = client['sports'] 
    collection = db['nhl']  # Replace 'your_collection_name' with your actual collection name

    try:
        collection.insert_many(records)
        print("Data saved to MongoDB")
    except Exception as e:
        print(f"Error saving data to MongoDB: {e}")
        raise
    finally:
        client.close()

# Define the default_args dictionary
default_args = {
    'owner': 'airflow',
    'start_date': datetime.now(),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate the DAG
dag = DAG(
    'scrape_nhl_data',
    default_args=default_args,
    description='Scrape NHL data from scrapethissite.com',
    schedule_interval=timedelta(days=1),
)

# Define the number of pages to scrape
page_limit = 4

# Create tasks dynamically for each page
for page in range(page_limit):
    scrape_task = PythonOperator(
        task_id=f'scrape_page_{page}',
        python_callable=scrape_page,
        op_kwargs={'page_num': page + 1},
        provide_context=True,
        dag=dag,
    )

    # Set up dependencies between tasks
    if page > 0:
        scrape_task.set_upstream(prev_scrape_task)

    prev_scrape_task = scrape_task

# Concatenate tables and save to CSV
concat_task = PythonOperator(
    task_id='concat_tables',
    python_callable=concat_tables,
    provide_context=True,
    dag=dag,
)

# Save to MongoDB task
save_to_mongodb_task = PythonOperator(
    task_id='save_to_mongodb',
    python_callable=save_to_mongodb,
    provide_context=True,
    dag=dag,
)

# Set up final dependencies
prev_scrape_task >> concat_task >> save_to_mongodb_task
