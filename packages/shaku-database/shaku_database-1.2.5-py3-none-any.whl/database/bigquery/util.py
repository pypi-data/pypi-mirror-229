import time
from typing import List

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


def get_table_info(dataset, table_name):
    client = bigquery.Client()
    # table_id = 'your-project.your_dataset.your_table'
    full_table_id = f'{dataset}.{table_name}'
    table = client.get_table(full_table_id)
    # print("Table schema: {}".format(table.schema))
    # print("Table description: {}".format(table.description))
    # print("Table has {} rows".format(table.num_rows))
    return table.schema


def validate_dataframe_type_with_bq(df, target_dataset, target_table):
    try:
        table_schema = get_table_info(target_dataset, target_table)
        for col_info in table_schema:
            if col_info.name in df.columns:
                if col_info.field_type == 'STRING':
                    df[col_info.name] = df[col_info.name].astype(str)
                    df.loc[df[col_info.name] == 'None', col_info.name] = None
                elif col_info.field_type == 'FLOAT':
                    df[col_info.name] = df[col_info.name].astype(float)
                elif col_info.field_type == 'INTEGER':
                    df[col_info.name] = df[col_info.name].astype('Int64')
                elif col_info.field_type == 'TIMESTAMP':
                    df[col_info.name] = pd.to_datetime(df[col_info.name])
                elif col_info.field_type == 'DATETIME':
                    df[col_info.name] = pd.to_datetime(df[col_info.name]).dt.tz_localize(None)
                else:
                    df[col_info.name] = df[col_info.name].astype(object)
                    df.loc[df[col_info.name] == 'None', col_info.name] = None
    except Exception as e:
        print("[ERROR] --> Convert column type error,or Key Error")
        raise e
    return df


def save_data_to_bq(insert_df, dataset_id, table_id, schema=None):
    try:
        client = bigquery.Client()
        # 資料表參數
        table_ref = client.dataset(dataset_id).table(table_id)
        job_config = bigquery.LoadJobConfig()
        if schema:
            job_config.schema = schema
        else:
            job_config.autodetect = True
        job = client.load_table_from_dataframe(insert_df, table_ref, job_config=job_config)
        job.result()
    except Exception as e:
        raise e


def query_multiple_data_from_bq(sql_list, data_name):
    try:
        client = bigquery.Client()
        result_dict = {}
        for sql, alias in zip(sql_list, data_name):
            results = client.query(sql)
            df = results.to_dataframe()
            result_dict[alias] = df
    except Exception as e:
        raise e
    return result_dict


def check_table_exist(table_id):
    client = bigquery.Client()

    try:
        client.get_table(table_id)  # Make an API request.
        print("Table {} already exists.".format(table_id))
    except NotFound:
        print("Table {} is not found.".format(table_id))


def create_table(table_name, columns, types, modes=None):
    client = bigquery.Client()

    if modes:
        schema = [bigquery.SchemaField(col, t, mode=mode) for col, t, mode in zip(columns, types, modes)]
    else:
        schema = [bigquery.SchemaField(col, t, mode="REQUIRED") for col, t in zip(columns, types)]
    table = bigquery.Table(table_name, schema=schema)
    table = client.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )


def merge_table(project_name: str, target_table: str, target_dataset, source_df: pd.DataFrame, unique_keys: List[str],
                update_cols: List[str] = None, exclude_update_col: List[str] = None):
    try:
        print("Start Merge Table")
        client = bigquery.Client()
        merge_sql = """MERGE {project_name}.{target_dataset}.{target_table} T
                        USING {project_name}.{target_dataset}.{target_table}_tmp S
                        ON {merge_condition}
                        WHEN MATCHED THEN
                        update set {match_sql}
                        WHEN NOT MATCHED THEN
                        INSERT ROW"""
        merge_condition = " and ".join([f"T.{col} = S.{col}" for col in unique_keys])
        if update_cols:
            match_sql = ",".join([f"T.{col} = S.{col}" for col in update_cols])
        elif exclude_update_col:
            match_sql = ",".join([f"T.{col} = S.{col}" for col in source_df.columns
                                  if col not in exclude_update_col or col not in unique_keys])
        else:
            match_sql = ",".join([f"T.{col} = S.{col}" for col in source_df.columns if col.lower() not in unique_keys])

        merge_sql = merge_sql.format(target_dataset=target_dataset, target_table=target_table,
                                     merge_condition=merge_condition, match_sql=match_sql, project_name=project_name)
        print(f"Merge SQL : {merge_sql}")
        source_df = validate_dataframe_type_with_bq(source_df, target_dataset, target_table)
        target_schema = get_table_info(target_dataset, target_table)
        print("Start create tmp table")
        save_data_to_bq(source_df, target_dataset, target_table + "_tmp", schema=target_schema)
        print("create tmp table End")
        print("Start merge")
        start = time.time()
        query_job = client.query(merge_sql)
        query_job.result()
        total_time = str(time.time()-start)
        print(f"End merge : {total_time} seconds")
        client.delete_table(f"{target_dataset}.{target_table}_tmp", not_found_ok=True)
    except Exception as e:
        print(e)
        print("[ERROR]--> Merge Table Error")
