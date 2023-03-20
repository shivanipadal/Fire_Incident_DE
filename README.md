# # Fire Incidents Analysis

## Data Engineering Zoomcamp Project

This repository contains my project for the completion of [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) by [DataTalks.Club](https://datatalks.club).

### Index
- [Problem Description](#problem-description)
- [Dataset](#dataset)
- [Technologies Used](#technologies-used)
- [Steps for Project Reproduction](#steps-for-project-reproduction)
- [Dashboard](#dashboard)
## Problem Description
A fire incident is defined as an incident involving smoke, heat, and flames.
The purpose of this simple project was to analyze the fire incidents dataset from USA

Below is the high level overview of the steps involved:
 * Download csv data from Source.
 * Upload the data to Data Lake by transforming csv into efficient parquet format.
 * Loading the data from Data Lake to Data Warehouse with some transformations and data quality checks.
 
 ## Dataset
The chosen dataset was the fire incidents data in the US from 1-Jan-2003 to 20-Mar-2023. 

It includes a summary of each (non-medical) incident to which the SF Fire Department responded. Each incident record includes, the incident number, the battalion whihc responded to the incident, the incident date, the timestamp of alarm, arrival and closure of the incident, among others. 

It is available for [download as a csv file](https://data.sfgov.org/api/views/wr8u-xric/rows.csv?accessType=DOWNLOAD) and for [consultation](https://data.sfgov.org/Public-Safety/Fire-Incidents/wr8u-xric) where it is also provided a [data dictionary](https://data.sfgov.org/api/views/wr8u-xric/files/54c601a2-63f1-4b27-a79d-f484c620f061?download=true&filename=FIR-0001_DataDictionary_fire-incidents.xlsx). As of 20-Mar-2023, this dataset is updated daily.

## Technologies Used

Below tools have been used for this project:
- **Infrastructure as code (IaC):** Terraform
- **Workflow orchestration:** Prefect
- **Data Lake:** Google Cloud Storage (GCS)
- **Data Warehouse:** BigQuery
- **Transformations:** dbt
- **Visualization:** Google Data Studio

## Steps for Project Reproduction
Clone this repo to start with.

### Step 1
Creation of a [Google Cloud Platform (GCP)](https://cloud.google.com/) account.

### Step 2: Setup of GCP 
- Creation of new GCP project. Attention: The Project ID is important. 
- [Create VM instance](#https://github.com/ABZ-Aaron/DataEngineerZoomCamp/blob/master/week_1_basics_n_setup/README.md#setting-up-a-cloud-vm-and-ssh-access) till 23rd step 
- Go to `IAM & Admin > Service accounts > Create service account`, provide a service account name and grant the roles `Viewer`, `BigQuery Admin`, `Storage Admin`, `Storage Object Admin`. 
- Download lservice account key locally, rename it to `google_credentials.json`. 
- Store it in your home folder `$HOME/.google/credentials/`for easier access. 
- Set and export the GOOGLE_APPLICATION_CREDENTIALS using `export GOOGLE_APPLICATION_CREDENTIALS=<path/to/your/service-account-authkeys>.json`
- Activate the service account using `gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS`
- Add the above two lines at the end of `.bashrc` so that we don't need to export and activate every time.
- Activate the following API's:
   * https://console.cloud.google.com/apis/library/iam.googleapis.com
   * https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com

### Step 3: Creation of a GCP Infrastructure
- [Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- Change default variables `project`, `region`, `BQ_DATASET` in `variables.tf` (the file contains descriptions explaining these variables)
- Run the following commands from terraform directory on bash:
```shell
# Initialize state file (.tfstate)
terraform init

# Check changes to new infra plan
terraform plan

# Create new infra
terraform apply
```
- Confirm in GCP console that the infrastructure was correctly created.

### Step 4: Creation of Conda environment and Orchestration using prefect flows.

#### Execution

**1.** Create a new Conda environment and install packages listed in  `prefect_ingest_data/requirements.txt` . 
```
conda create -n <env_name> python=3.9
conda activate <env_name>
pip install -r prefect_ingest_data/requirements.txt
```
**2.** Register Prefect blocks and start Orion

```
prefect block register-m prefect_gcp
prefect orion start
```
* Navigate to prefect dashboard `http://127.0.0.1:4200` --> go to blocks menu --> add `GCS Bucket` and provide below inputs.
	* Block name : `<your-GCS-bucket-block-name>`
	* Bucket name: `<your-bucket-name-created-by-terraform>`
	* GCP credentials:  Click on Add --> It opens up create block of GCP credentials , provide input below.
		* Block name : `<your-GCP-credentials-block-name>`
		* Service Account info: copy paste the json file data in the service account info.
		* Clicck on create.
	* GCP credentials:  Click on Add --> Select the above created `<your-GCP-credentials-block-name>`
	* Code generated needs to be replaced in the `web-to-gcs-parent.py` and `gcs_to_bq_parent`python files.
		```
		from prefect_gcp.cloud_storage import GcsBucket
		gcp_cloud_storage_bucket_block = GcsBucket.load("<your-gcp-bucket-block-name")

		from prefect_gcp import GcpCredentials
		gcp_credentials_block = GcpCredentials.load("<your-gcs-cred-block-name>")

		```    
**3.**  Change the directory to prefect_ingest_data and run below command to deploy code in prefect 
```
prefect deployment build ./ingest_data_to_bucket.py:ingest_data_to_bucket -n "Ingest data from web to gcs bucket" --cron "0 0 1 * *" -a

prefect deployement build ./ingest_data_to_bq.py:ingest_data_to_bq -n "Ingest data from gcs bucket to bigquery" --cron "0 1 1 * *" -a
```
**4.** Navigate to prefect deployment dashboard and check for the recently created deployments. 
[Image](https://github.com/shivanipadal/Fire_Incident_DE/blob/main/images/deploy_code.png)

**5.** Run deployments from prefect dashboard

The above deployments download csv data from web portal  and stores it into GCS bucket as .parquet file and then writes data into Google BigQuery.

### Step 5: Transformations using dbt.

* Navigate to [dbt cloud](https://www.getdbt.com/) and create a new project by referring to this repository. Under the project subfolder update `/dbt`
* Select the BigQuery connection and update `service-account.json` file for the authentication. 
* Under dbt development menu, edit the `dbt-project.yml` to update the `name` and `models`.
* add [macros/extract_month_with_name.sql](https://github.com/shivanipadal/DE_projects/tree/main/Project2/dbt/macros),   [models/core/schema.yml](https://github.com/shivanipadal/Fire_Incident_DE/blob/main/dbt/models/core/schema.yml), [models/core/stg_fire_accident.sql](https://github.com/shivanipadal/Fire_Incident_DE/blob/main/dbt/models/core/stg_fire_accident.sql), [packages.yml](https://github.com/shivanipadal/Fire_Incident_DE/blob/main/dbt/packages.yml)
* Run below commands to execute the transformations:
	```
	dbt deps
	dbt build
	``` 
	[Image](https://github.com/shivanipadal/Fire_Incident_DE/blob/main/images/dbt.png)
* The above will create dbt models and final tables
   **Note**: The transformations made were the selection of certain columns and creation of new ones (time differences, Month, Year). It is known that tables with less than 1 GB don't show significant improvement with partitioning and clustering; doing so in a small table could even lead to increased cost due to the additional metadata reads and maintenance needed for these features (or) the processing data clustered and with out clustered is same for small data

As of 20-Mar-2023, the dataset has a size of ~ 260 MB, thus I only performed transformations such as adding new variables, and not partitioning and clustering.

```sql
CREATE  OR  REPLACE  TABLE  `de-project-2023.fire_accident_raw_data.fire_data_sanfrancisco_clustered`

Cluster  BY

Battalion AS

SELECT  *  FROM de-project-2023.fire_accident_raw_data.fire_data_sanfrancisco;
```

...makes the query same data...
[Dashboard](https://github.com/shivanipadal/Fire_Incident_DE/blob/main/images/clustered_table.png)

as performing it on the not clustered table.
[Dashboard](https://github.com/shivanipadal/Fire_Incident_DE/blob/main/images/normal_table.png)

 ### Step 6: Development of a visualization using lookerstudio

 * Connect the final BigQuery dataset from above inside lookerstudio and start creating the dashboard with insights. 
 
 ## Dashboard

Below is the final [dashboard](https://lookerstudio.google.com/reporting/16920cba-f313-43f9-a4eb-7fd6cdb0dd19/page/hKJJD)

[Dashboard_pdf_link](https://github.com/shivanipadal/Fire_Incident_DE/blob/main/Dashboard/Fire_Incident_Report.pdf)

[Dashboard Image]
(https://github.com/shivanipadal/Fire_Incident_DE/blob/main/images/Dashboard.jpg)

**A special thank you to [DataTalks.Club](https://datatalks.club) for providing this incredible course! Also, thank you to the amazing slack community!**
