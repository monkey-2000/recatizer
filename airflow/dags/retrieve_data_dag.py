#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import timedelta
from pathlib import Path

from airflow import DAG
import logging

from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'email': ['em@il.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

PROJECT_ROOT = os.getenv('PROJECT_ROOT')
if PROJECT_ROOT is None:
    logger.info('no $PROJECT_ROOT provided\tuse /opt/airflow')
    PROJECT_ROOT = '/opt/airflow'
PROJECT_ROOT = Path(PROJECT_ROOT)

DATA_DIR_PATH = PROJECT_ROOT / 'data'
# RAW_DATA_PATH = DATA_DIR_PATH / 'raw'
RETRIEVED_DATA_PATH = DATA_DIR_PATH / 'retrieved'

images_list = []


def _get_images_list():
    global images_list
    images_list.clear()
    # todo: make request to mongo


with DAG(dag_id='retrieve_data',
         default_args=default_args,
         schedule_interval='@daily',
         start_date=days_ago(5)) as dag:
    task_1 = PythonOperator(task_id='get_image_list',
                            python_callable=_get_images_list,
                            op_kwargs={})
