from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from random import randint
from datetime import datetime
import os


@task()
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read Fire accident data from web into pandas DataFrame"""

    df = pd.read_csv(dataset_url,low_memory=False)
    # print(df.head)  
    # print(df.dtypes)
    # remove spaces in the column name
    df.columns = df.columns.str.replace(' ', '')
    # exit()  
    return df

@task()
def write_local(df: pd.DataFrame, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""
    if not os.path.exists('data'): 
        os.makedirs('data')

    path = Path(f"data/{dataset_file}.parquet")
    df.to_parquet(path)
    return path


@task()
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""
    gcs_block = GcsBucket.load("de-project-gcs")
    gcs_block.upload_from_path(from_path=path, to_path=path)
    return


@flow()
def ingest_data_to_bucket() -> None:
    """The main ETL function"""

    dataset_url = "https://data.sfgov.org/api/views/wr8u-xric/rows.csv?accessType=DOWNLOAD"
    dataset_file = "fire_incidents.csv"
    df = fetch(dataset_url)
    path = write_local(df, dataset_file)
    write_gcs(path)


if __name__ == "__main__":
    ingest_data_to_bucket()

