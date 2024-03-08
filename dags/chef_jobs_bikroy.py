from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from selenium import webdriver
import pandas as pd
import time
from pymongo import MongoClient

# MongoDB connection URL
mongo_url = 'mongodb://host.docker.internal:27017/'

# Set Chrome options for headless mode
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')

# DAG configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'chef_jobs_bikroy',
    default_args=default_args,
    schedule_interval='@monthly',  # Set your desired schedule
    catchup=False,
)

def navigate_to_chef_jobs(**kwargs):
    job_listings_path = '//div[@class="ad-list-container--1UnyA"]//a[@data-testid="ad-card-link"]'
    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get('https://bikroy.com/')
        time.sleep(3)
        try:
            driver.find_element('xpath', '//p[text()="Jobs"]').click()
            time.sleep(3)
            driver.find_element('xpath', '//span[text()="Chef"]').click()
            time.sleep(3)
        except Exception as e:
            print(f"Error navigating to Jobs or Chef section: {e}")
            raise
        # Start crawling listings
        try:
            job_listings = driver.find_elements('xpath', job_listings_path)
        except Exception as e:
            print(f"Error finding job listings: {e}")
            raise

        all_jobs = []

        for each_job in job_listings:
            job_title = each_job.find_element('xpath', './/h2').text
            company = each_job.find_element('xpath', './/h2/following::*/div').text

            try:
                salary = each_job.find_element('xpath', './/div[@class="price--3SnqI color--t0tGX"]').text
            except Exception:
                salary = None

            city, category = each_job.find_element('xpath', './/div[@class="description--2-ez3"]').text.split(',')
            updated_time = each_job.find_element('xpath', './/div[@class="updated-time--1DbCk"]').text
            last_checked = datetime.now()

            data = {
                'job_title': job_title,
                'company': company,
                'salary': salary,
                'city': city,
                'category': category.strip(),
                'updated_time': updated_time,
                'last_checked': last_checked
            }
            all_jobs.append(data)

    # Push data to XCom
    kwargs['ti'].xcom_push(key='chef_jobs_data', value=all_jobs)

def save_to_csv(**kwargs):
    ti = kwargs['ti']
    all_jobs = ti.xcom_pull(task_ids='navigate_to_chef_jobs', key='chef_jobs_data')

    dataframe = pd.DataFrame(all_jobs)
    try:
        dataframe.to_csv('/opt/airflow_app/output/chef_jobs.csv', encoding='utf-16', sep='\t', index=False)
        print("Job data saved successfully.")
    except Exception as e:
        print(f"Error saving job data to CSV: {e}")
        raise

def save_to_mongodb(**kwargs):
    ti = kwargs['ti']
    all_jobs = ti.xcom_pull(task_ids='navigate_to_chef_jobs', key='chef_jobs_data')

    # Convert the list of dictionaries to a DataFrame
    dataframe = pd.DataFrame(all_jobs)

    # Save DataFrame to MongoDB
    client = MongoClient(mongo_url)
    db = client['jobs']  # Replace 'your_database_name' with your actual database name
    collection = db['chef_jobs']

    try:
        records = dataframe.to_dict(orient='records')
        collection.insert_many(records)
        print("Job data saved to MongoDB successfully.")
    except Exception as e:
        print(f"Error saving job data to MongoDB: {e}")
        raise
    finally:
        client.close()


# Define tasks
navigate_task = PythonOperator(
    task_id='navigate_to_chef_jobs',
    python_callable=navigate_to_chef_jobs,
    dag=dag,
    provide_context=True,
)

save_task = PythonOperator(
    task_id='save_to_csv',
    python_callable=save_to_csv,
    provide_context=True,
    dag=dag,
)

save_mongodb_task = PythonOperator(
    task_id='save_to_mongodb',
    python_callable=save_to_mongodb,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
navigate_task >> save_task >> save_mongodb_task

if __name__ == "__main__":
    dag.cli()