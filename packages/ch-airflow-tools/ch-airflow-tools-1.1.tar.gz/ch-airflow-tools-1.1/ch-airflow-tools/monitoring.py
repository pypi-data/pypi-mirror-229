from airflow.models import TaskInstance

def get_task_status(dag, task_id, execution_date):
    """
    Get the status of a task for a specific execution date in a DAG.

    Args:
        dag (DAG): The DAG object.
        task_id (str): The task ID.
        execution_date (str): The execution date in ISO8601 format.

    Returns:
        str: Task status (e.g., "success", "failed", "running", "skipped").
    """
    task_instance = TaskInstance(dag.get_task(task_id=task_id), execution_date)
    
    if task_instance.current_state() is None:
        return "not_executed"
    
    return task_instance.current_state()
