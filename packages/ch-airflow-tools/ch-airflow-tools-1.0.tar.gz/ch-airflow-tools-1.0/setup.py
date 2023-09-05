from setuptools import setup

setup(name='ch-airflow-tools',
      version='1.0',
      description='Apache Airflow tools',
      author='Alex Yung',
      packages=['ch-airflow-tools'],
      zip_safe=False,
      install_requires=[
        'airflow',
    ],)