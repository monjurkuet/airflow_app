from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pymongo import MongoClient

# MongoDB connection URL
mongo_url = 'mongodb://host.docker.internal:27017/'

# Define default_args dictionary to specify the default parameters of the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate the DAG
dag = DAG(
    'crawl_country_data',
    default_args=default_args,
    schedule_interval='0 0 * * 0',  # Set the schedule interval based on your requirements
)

def fetch_html_content(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML content: {e}")
        raise

def extract_countries_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    countries_div = soup.find('section', {'id': 'countries'})
    rows = countries_div.find_all('div', {'class': 'col-md-4 country'})
    
    countries_data = []

    for country_div in rows:
        country_name = country_div.find('h3', {'class': 'country-name'}).text.strip()
        capital = country_div.find('span', {'class': 'country-capital'}).text.strip()
        population = country_div.find('span', {'class': 'country-population'}).text.strip()
        area = country_div.find('span', {'class': 'country-area'}).text.strip()
        
        country_info = {
            'Country Name': country_name,
            'Capital': capital,
            'Population': population,
            'Area': area,
            'Area Unit': 'km2',
        }
        
        countries_data.append(country_info)

    return countries_data

def save_to_csv(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='scrape_and_process_data')
    output_path = '/opt/airflow_app/output/countries_data.csv'

    try:
        df.to_csv(output_path, encoding='utf-16', sep='\t', index=False)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        raise

def save_to_mongodb(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='scrape_and_process_data')

    # Convert the DataFrame to a MongoDB-friendly format
    records = df.to_dict(orient='records')

    # Save to MongoDB
    client = MongoClient(mongo_url)
    db = client['country_data']  # Replace 'your_database_name' with your actual database name
    collection = db['stats']

    try:
        collection.insert_many(records)
        print("Data saved to MongoDB")
    except Exception as e:
        print(f"Error saving data to MongoDB: {e}")
        raise
    finally:
        client.close()

# Task: Save DataFrame to CSV
save_to_csv_task = PythonOperator(
    task_id='save_to_csv',
    python_callable=save_to_csv,
    provide_context=True,
    dag=dag,
)

# Task: Save DataFrame to MongoDB
save_to_mongodb_task = PythonOperator(
    task_id='save_to_mongodb',
    python_callable=save_to_mongodb,
    provide_context=True,
    dag=dag,
)

# Define the function to scrape and process data
def scrape_and_process_data(**kwargs):
    headers = {
        'authority': 'www.scrapethissite.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-GB,en;q=0.5',
        'cache-control': 'max-age=0',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    url = 'https://www.scrapethissite.com/pages/simple/'

    html_content = fetch_html_content(url, headers)

    countries_data = extract_countries_data(html_content)

    df = pd.DataFrame(countries_data)

    return df

# Task: Scrape and process data
scrape_and_process_data_task = PythonOperator(
    task_id='scrape_and_process_data',
    python_callable=scrape_and_process_data,
    provide_context=True,
    dag=dag,
)

# Set the task dependencies
scrape_and_process_data_task >> [save_to_csv_task, save_to_mongodb_task]

if __name__ == "__main__":
    dag.cli()
