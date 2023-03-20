from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials


@task()
def extract_from_gcs(file: str) -> Path:
    """Download fire data from GCS"""
    gcs_path = f"data/{file}"
    gcs_block = GcsBucket.load("de-project-gcs")
    
    gcs_block.get_directory(from_path=gcs_path, local_path=f"../data/")
    return Path(f"../data/{gcs_path}")


@task()
def write_bq(path: Path,file: str) -> int:
    """Write DataFrame to BiqQuery"""

    df = pd.read_parquet(path)

    gcp_credentials_block = GcpCredentials.load("gcp-creds-project")

    # print(df.head())
    # print(df.columns)

    df.to_gbq(
        destination_table="fire_accident_raw_data.fire_data_sanfrancisco",
        project_id="de-project-2023",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
    )
    
    return len(df)

@flow(log_prints=True)
def etl_gcs_to_bq(file):
    """Main ETL flow to load data into Big Query"""

    path = extract_from_gcs(file)
    #df = transform(path)
    records=write_bq(path,file)

    return records

@flow(log_prints=True)
def ingest_data_bq(
    file: str = 'fire_incidents.csv.parquet'
    ):
    rec_count=etl_gcs_to_bq(file)

    print("Total no of records processed", rec_count)

if __name__ == "__main__":
    file='fire_incidents.csv.parquet'
    ingest_data_bq(file)
