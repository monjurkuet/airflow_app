from datetime import datetime
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

def resolve_conflict(**kwargs):
    # Check if today is the first day of the month
    if datetime.now().day == 1:
        # Trigger DAG-1 with specific conf parameters
        trigger_dag1_op = TriggerDagRunOperator(
            task_id='trigger_dag1',
            trigger_dag_id='scrapethissite_tasks',
            conf={'dag_run_order': kwargs['dag_run'].run_id},
            dag=kwargs['dag'],
        )
        trigger_dag1_op.execute(kwargs)
