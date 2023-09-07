import datetime
from structured_logging.logging import set_logger
from airflow import DAG
from airflow.models import TaskInstance
from airflow.utils.dates import days_ago
from airflow.exceptions import AirflowException

def get_task_logs(dag_id, task_id, execution_date):
    try:
        dag = DAG(dag_id=dag_id, start_date=days_ago(1))
        task_instance = TaskInstance(task=dag.get_task(task_id), execution_date=execution_date)
        logs = task_instance.log_entries
        return logs
    except AirflowException as e:
        return str(e)
    
def get_dag_logs(dag_id, execution_date):
    try:
        dag = DAG(dag_id=dag_id, start_date=days_ago(1))
        task_logs = {}

        for task in dag.tasks:
            task_instance = TaskInstance(task=task, execution_date=execution_date)
            logs = task_instance.log_entries
            task_logs[task.task_id] = logs

        return task_logs
    except AirflowException as e:
        return str(e)

def wrap_logger_airflow(filename):
    set_logger(filename)

def add_timestamp(_, __, event_dict):
        event_dict['timestamp'] = datetime.datetime.utcnow()
        return event_dict

