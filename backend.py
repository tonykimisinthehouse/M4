import time
from typing import Union
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
from configs import pg_connection_dict, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

from sql_generators import *

from skimage.metrics import structural_similarity
import cv2
import numpy as np

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
    # Connect to your postgres DB
    conn = psycopg2.connect(**pg_connection_dict)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    time_column = 'epoch'
    value_column = 'price'

    start_time = time.perf_counter()
    sql_query = f"""
    WITH Q AS ({select_query_raw_time_series('jrufjdm3qog6zerz_w_epoch', time_column, value_column, from_time, to_time)}),
    QC AS (SELECT count(*) as c from Q)
    SELECT * FROM Q WHERE (SELECT c FROM QC) <= {4 * chart_width} UNION
    SELECT * FROM (
    {sql_m4_aggregation("Q", time_column, value_column, from_time, to_time, chart_width)}
    ) AS QD wHERE (SELECT c FROM QC) > {4 * chart_width} ORDER BY {time_column}
    """
    cur.execute(sql_query)

    # Retrieve query results
    records = cur.fetchall()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    return {"records": records, "query_execution_time": elapsed_time}


@app.get("/get_raw_time_series")
def time_series_query_for_visualization(from_time: int, to_time: int):
    # Connect to your postgres DB
    conn = psycopg2.connect(**pg_connection_dict)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    time_column = 'epoch'
    value_column = 'price'

    start_time = time.perf_counter()
    cur.execute(f"""
    {select_query_raw_time_series('jrufjdm3qog6zerz_w_epoch', time_column, value_column, from_time, to_time)}
    """)

    # Retrieve query results
    records = cur.fetchall()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    return {"records": records, "query_execution_time": elapsed_time}


@app.post("/compute_dssim")
async def compute_dssim(image_1: UploadFile = File(...), image_2: UploadFile = File(...)):
    print(image_1.content_type)
    image_1_content = await image_1.read()
    image_2_content = await image_2.read()
    image_1_np_arr = np.fromstring(image_1_content, np.uint8)
    print(image_1_np_arr.shape)
    image_2_np_arr = np.fromstring(image_2_content, np.uint8)
    print(image_2_np_arr.shape)
    np.savetxt('test1.txt', image_1_np_arr, fmt='%d')
    np.savetxt('test2.txt', image_2_np_arr, fmt='%d')

    image_1_cv2 = cv2.imdecode(image_1_np_arr, cv2.IMREAD_COLOR)
    image_2_cv2 = cv2.imdecode(image_2_np_arr, cv2.IMREAD_COLOR)
    print(image_1_cv2.shape)
    print(image_2_cv2.shape)

    # Convert images to grayscale
    image_1_gray = cv2.cvtColor(image_1_cv2, cv2.COLOR_BGR2GRAY)
    image_2_gray = cv2.cvtColor(image_2_cv2, cv2.COLOR_BGR2GRAY)
    (ssim, diff) = structural_similarity(image_1_gray, image_2_gray, full=True)
    dssim = (1 - ssim) / 2
    return {
        "dssim": dssim,
        "ssim": ssim
    }

from pydantic import BaseModel


class VisualizationQualityRecord(BaseModel):
    num_of_underlying_rows: int
    dssim: float
    ssim: float


@app.post("/record_visualization_quality")
async def record_visualization_quality(num_of_underlying_rows: int, dssim: float, ssim: float):
    url: str = SUPABASE_URL
    key: str = SUPABASE_KEY
    supabase: Client = create_client(url, key)
    data = supabase.table("visualization_quality")\
        .insert(
        {"num_of_underlying_rows" :  num_of_underlying_rows,
         "dssim": dssim,
         "ssim": ssim
         }
    ).execute()


@app.post("/record_query_performance")
async def record_query_performance(num_of_underlying_rows: int,
                                   base_execution_time: float, base_total_time: float,
                                   m4_execution_time: float, m4_total_time: float,
                                   ):
    url: str = SUPABASE_URL
    key: str = SUPABASE_KEY
    supabase: Client = create_client(url, key)
    data = supabase.table("query_performance")\
        .insert(
        {"num_of_underlying_rows":  num_of_underlying_rows,
         "base_query_execution_time": base_execution_time,
         "base_total_time": base_total_time,
         "m4_query_execution_time": m4_execution_time,
         "m4_total_time": m4_total_time,
         }
    ).execute()
