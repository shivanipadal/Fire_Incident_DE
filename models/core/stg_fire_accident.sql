{{ config(materialized='table') }}

select 
  incidentnumber,
  id,
  address,
  cast(incidentdate as DATETIME) as incidentdate,
  extract(year from cast(incidentdate as DATETIME)) as incidentyear,
  extract(month from cast(incidentdate as DATETIME)) as incidentmonth,
  {{ extract_month_with_name('extract(month from cast(incidentdate as DATETIME))') }} as incidentmonth_with_name,
  cast(alarmdttm as DATETIME) as alarmdttm,
  cast(arrivaldttm as DATETIME) as arrivaldttm,
  TIMESTAMP_DIFF(cast(arrivaldttm as TIMESTAMP), cast(alarmdttm as TIMESTAMP),MINUTE) as delay_arrival_sec,
  cast(closedttm as DATETIME) as closedttm,
  city,
  zipcode,
  battalion,
  stationarea,
  numberofalarms,
  actiontakenprimary,
  actiontakensecondary,
  actiontakenother

  from 
    {{ source('staging', 'fire_data_sanfrancisco')}}
