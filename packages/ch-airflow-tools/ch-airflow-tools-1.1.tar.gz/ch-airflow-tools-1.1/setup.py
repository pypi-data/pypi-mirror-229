from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='ch-airflow-tools',
      version='1.1',
      description='Apache Airflow tools',
      author='Alex Yung',
      packages=['ch-airflow-tools'],
      zip_safe=False,
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=[
        'apache-airflow',
    ],)