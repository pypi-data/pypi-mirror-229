from airflow import DAG
from airflow.models import DagRun, TaskInstance
from airflow.utils.dates import days_ago
from airflow.exceptions import AirflowException

def get_sla_misses(dag_id, execution_date):
    try:
        dag = DAG(dag_id=dag_id, start_date=days_ago(1))
        dagrun = DagRun.find(dag_id=dag_id, execution_date=execution_date)
        
        if dagrun:
            sla_misses = []
            for task_instance in dagrun.get_task_instances():
                if task_instance.state == 'failed' and task_instance.sla_miss:
                    sla_misses.append({
                        "task_id": task_instance.task_id,
                        "execution_date": task_instance.execution_date,
                        "sla": task_instance.task.sla,
                    })
            return sla_misses
        else:
            return []
    except AirflowException as e:
        return str(e)
    
def get_task_retries(dag_id, task_id, execution_date):
    try:
        dag = DAG(dag_id=dag_id, start_date=days_ago(1))
        task_instance = TaskInstance(task=dag.get_task(task_id), execution_date=execution_date)
        
        # Retrieve the number of retries (try_number)
        retries = task_instance.try_number
        return retries
    except AirflowException as e:
        return str(e)