# Airflow Tools

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Welcome to Airflow Tools! This package provides a collection of useful tools, utilities, and extensions for working with Apache Airflow, a platform to programmatically author, schedule, and monitor workflows.

## Features

- **Task Monitoring:** Monitor task statuses and execution details easily.
- **Utilities:** Helpful utility functions to simplify common Airflow tasks.
- **Extensions:** Additional features and integrations to enhance your Airflow workflows.

## Installation

You can install `ch-airflow-tools` using pip:

```bash
pip install ch-airflow-tools
```

## Usage
Once installed, you can import and use the tools provided by this package in your Airflow DAGs and workflows. Here's a quick example of using the task monitoring feature:

```python
from airflow import DAG
from airflow_tools.monitoring import get_task_status

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 1),
    'retries': 1,
}

dag = DAG('example_dag', default_args=default_args, schedule_interval='@daily')

# Define your tasks here...

# Example of using the task monitoring function
task_status = get_task_status(dag=dag, task_id='my_task_id', execution_date='2023-08-22T00:00:00+00:00')
print("Task Status:", task_status)
```

## Contributing
Contributions are welcome! If you have an idea for a new feature, find a bug, or want to improve the documentation, feel free to open an issue or submit a pull request. Please make sure to follow the contribution guidelines when contributing.

## License
This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
