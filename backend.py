import time
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
from configs import pg_connection_dict
from sql_generators import *
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/get_time_series")
def time_series_query_for_visualization(from_time: int, to_time: int, chart_width: int, chart_height: int):
    start_time = time.perf_counter()
    # Connect to your postgres DB
    conn = psycopg2.connect(**pg_connection_dict)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    time_column = 'epoch'
    value_column = 'price'

    sql_query = f"""
    WITH Q AS ({select_query_raw_time_series('jrufjdm3qog6zerz_w_epoch', time_column, value_column, from_time, to_time)}),
    QC AS (SELECT count(*) as c from Q)
    SELECT * FROM Q WHERE (SELECT c FROM QC) <= {4 * chart_width} UNION
    SELECT * FROM (
    {sql_m4_aggregation("Q", time_column, value_column, from_time, to_time, chart_width)}
    ) AS QD wHERE (SELECT c FROM QC) > {4 * chart_width}
    """
    print(sql_query)
    cur.execute(sql_query)

    # Retrieve query results
    records = cur.fetchall()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time)

    return records


@app.get("/get_raw_time_series")
def time_series_query_for_visualization(from_time: int, to_time: int):
    start_time = time.perf_counter()
    # Connect to your postgres DB
    conn = psycopg2.connect(**pg_connection_dict)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    time_column = 'epoch'
    value_column = 'price'

    cur.execute(f"""
    {select_query_raw_time_series('jrufjdm3qog6zerz_w_epoch', time_column, value_column, from_time, to_time)}
    """)

    # Retrieve query results
    records = cur.fetchall()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time)

    return records



